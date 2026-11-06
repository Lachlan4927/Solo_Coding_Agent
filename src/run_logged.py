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
    sys.exit("Choose single or multi.")

os.environ["PYTHONIOENCODING"] = "utf-8" 

started = time.time()
output = ""

print("Running...", flush=True)

process = subprocess.Popen(
    [sys.executable, "-u", "-B", str(project / "src" / script)],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
    errors="replace",
    cwd=project,
)

process.stdin.write(task + "\n")
process.stdin.close()

for line in process.stdout:
    print(line, end="", flush=True)
    output += line

process.wait()

record = {
    "task_id": task_id,
    "mode": mode,
    "task": task,
    "seconds": round(time.time() - started, 2),
    "exit_code": process.returncode,
    "output": output,
    "errors": "",
}

folder = project / "runtime" / "logs"
folder.mkdir(parents=True, exist_ok=True)

with open(folder / "runs.jsonl", "a", encoding="utf-8") as file:
    file.write(json.dumps(record, ensure_ascii=False) + "\n")

print("Saved to runtime/logs/runs.jsonl")