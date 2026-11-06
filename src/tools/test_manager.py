from pathlib import Path

from smolagents import tool

from .file_manager import workspace_folder


@tool
def write_test_file(path: str, content: str) -> str:
    """
    Create or replace a Python test file.
    Paths are relative to the workspace root and must include tests/.
    Missing parent directories are created automatically.
    This tool saves the file; use execute_file to run it.

    Args:
        path: Relative test path including tests/, such as tests/test_solution.py. Do not supply a bare filename, an absolute path, or a runtime/ or workspace/ prefix.
        content: Complete Python unittest source code, including imports, test methods and an if __name__ == "__main__": unittest.main() entry point.
    """
    try:
        workspace = Path(workspace_folder).resolve()
        tests_folder = (workspace / "tests").resolve()
        requested = Path(path)

        if requested.is_absolute() or requested.suffix != ".py":
            return "error: use tests/test_solution.py"

        target = (workspace / requested).resolve()

        if not tests_folder.is_relative_to(workspace):
            return "error: tests folder is outside the workspace"

        if not target.is_relative_to(tests_folder):
            return "error: save tests inside tests/, e.g. tests/test_solution.py"

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

        return "saved test file: " + target.relative_to(workspace).as_posix()

    except Exception as error:
        return "error: " + str(error)