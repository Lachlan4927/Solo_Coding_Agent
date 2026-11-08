import re  # regex to parse agent reports and recover files on api error not tool call common with grok

from smolagents import tool
from smolagents.utils import AgentGenerationError
from tools.code_executor import run_file
import os
from tools.file_manager import get_safe_path


class Coordinator:

    def __init__(self, coder, tester):
        self.coder = coder
        self.tester = tester 
        self.test_runs = {}
        self.coder_files = set()
        original_write_file = self.coder.tools["write_file"]




        @tool
        def write_file(path: str, content: str) -> str:
            """
            Write an implementation file and remember its path.

            Args:
                path: File path relative to the workspace.
                content: Complete file contents.
            """
            result = original_write_file(path, content)

            if result.startswith("saved file:"):
                self.coder_files.add(path)

            return result

        self.coder.tools["write_file"] = write_file




        @tool
        def execute_file(path: str) -> str:
            """
            Run a Python test file in Docker.

            Args:
                path: Test file inside the workspace.
            """
            result = run_file(path)
            self.test_runs[path] = result
            return (
                str(result["success"])
                + "\nstdout:\n" + result["stdout"]
                + "\nstderr:\n" + result["stderr"]
            )

        self.tester.tools["execute_file"] = execute_file






    def run_worker(self, worker, task):
        if worker.name == "coder":
            self.coder_files.clear()

        try:
            report = worker.run(task)

        except AgentGenerationError as error:
            message = str(error)
               
            if (
                worker.name == "tester"
                and "400" in message
                and "tool_use_failed" in message
                and self.tests_passed()
            ):
                evidence = []

                for path, result in self.test_runs.items():
                    evidence.append(
                        path
                        + "\nstdout:\n" + result["stdout"]
                        + "\nstderr:\n" + result["stderr"]
                    )

                return (
                    "PASS\n"
                    "Recorded unittest executions passed. "
                    "The Tester's closing response failed.\n"
                    + "\n".join(evidence)
                )

            recoverable = (
                worker.name == "coder"
                and "400" in message
                and "tool_use_failed" in message
            )

            if not recoverable:
                raise

            paths = [
                path
                for path in sorted(self.coder_files)
                if os.path.isfile(get_safe_path(path))
            ]

            if not paths:
                raise

            print("\nCoder response failed. Sending saved files to Tester.")

            return (
                "Unverified implementation. The Coder encountered a tool-call error.\n"
                "Files written during this attempt:\n"
                + "\n".join(paths)
                + "\nIndependently check the original requirements and test these files."
            )

        finished = any(
            getattr(step, "is_final_answer", False)
            for step in worker.memory.steps
        )

        if not finished:
            raise RuntimeError(worker.name + " reached its step limit.")

        return str(report)

        

    def tests_passed(self):
        if not self.test_runs:
            return False

        for result in self.test_runs.values():
            output = result["stdout"] + "\n" + result["stderr"]
            count = re.search(r"Ran (\d+) tests?", output)

            if not result["success"] or result["exit_code"] != 0:
                return False

            if count is None or int(count.group(1)) == 0:
                return False

            if not re.search(r"^OK\s*$", output, re.MULTILINE):
                return False

        return True



    def run(self, task):
        feedback = ""

        try:
            # Initial implementation, then at most one repair.
            for attempt in range(2):
                print("\nCoding attempt", attempt + 1)

                code_report = self.run_worker(
                    self.coder,
                    "Original task:\n" + task
                    + "\n\nPrevious test feedback:\n" + feedback,
                )

                self.test_runs.clear()

                test_report = self.run_worker(
                    self.tester,
                    "Original task:\n" + task
                    + "\n\nCoder report:\n" + code_report,
                )

                verdict = test_report.strip().splitlines()[0]

                if verdict == "PASS" and self.tests_passed():
                    return "VERIFIED\n" + test_report

                if verdict != "FAIL":
                    return "UNVERIFIED\n" + test_report

                feedback = test_report

            return "FAILED after one repair.\n" + feedback

        except AgentGenerationError as error:
            return "STOPPED: model/API error. No further delegation.\n" + str(error)

        except RuntimeError as error:
            return "STOPPED: " + str(error)