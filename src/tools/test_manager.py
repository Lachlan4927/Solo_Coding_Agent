from pathlib import Path

from smolagents import tool

from .file_manager import workspace_folder


@tool
def write_test_file(path: str, content: str) -> str:
    """
    Write a Python test inside the workspace's tests folder.

    Args:
        path: Workspace-relative path, such as tests/test_solution.py.
        content: Complete Python test code.
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