import json
import os
import subprocess
import sys
import time
from pathlib import Path


project = Path(__file__).resolve().parent.parent

mode = input("single or multi: ").strip()
task_id = input("task ID: ").strip()
task = input("coding task: ").strip()

if mode == "single":
    script = "run_single_agent.py"
elif mode == "multi":
    script = "run_multi_agent.py"
else:
    print("Choose single or multi.")
    sys.exit()

os.environ["CODING_TASK"] = task
os.environ["PYTHONIOENCODING"] = "utf-8"

started = time.time()
print("Running... output will appear when finished.")

result = subprocess.run(
    [sys.executable, "-u", "-B", str(project / "src" / script)],
    input=task + "\n",
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    cwd=project,
)

print(result.stdout)
print(result.stderr)

record = {
    "task_id": task_id,
    "mode": mode,
    "task": task,
    "seconds": round(time.time() - started, 2),
    "exit_code": result.returncode,
    "output": result.stdout,
    "errors": result.stderr,
}

folder = project / "runtime" / "logs"
folder.mkdir(parents=True, exist_ok=True)

with open(folder / "runs.jsonl", "a", encoding="utf-8") as file:
    file.write(json.dumps(record) + "\n")

print("Saved to runtime/logs/runs.jsonl")