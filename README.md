# Coding Assistant: Single-Agent and Multi-Agent Evaluation

A Python coding assistant built with `smolagents`, with a local browser interface served by Express. The project provides a single-agent baseline and a multi-agent workflow that separates implementation and testing. Both modes use the same configured language model and execute generated Python code in Docker.

The intended tasks are small, noninteractive Python programs using the standard library, such as arithmetic functions, string processing, and list operations.

## How it works

| Mode | Workflow | Limits |
| --- | --- | --- |
| Single agent | One agent writes the implementation, creates tests, executes them, and attempts repairs. | 16 agent steps. |
| Multi-agent | A Python coordinator calls a Coder, then a Tester. A failing test report can trigger one implementation repair and another test attempt. | Up to two coding/testing attempts; 10 Coder steps and 6 Tester steps per invocation. |

The coordinator is ordinary Python control logic, not a third language-model agent. Both modes use the configuration in `src/agents/agent_setup.py`:

| Setting | Gemini configuration | Groq configuration |
| --- | --- | --- |
| Provider endpoint | `https://generativelanguage.googleapis.com/v1beta/openai/` | `https://api.groq.com/openai/v1` |
| Model ID | `gemini-3.5-flash-lite` | `openai/gpt-oss-120b` |
| API-key variable | `GEMINI_API_KEY` | `GROQ_API_KEY` |
| Temperature | `0.1` | `0.1` |
| Reasoning effort | `low` | `low` |
| Maximum response tokens | `2048` | `2048` |

The supplied configuration selects Gemini. To use Groq, update the model ID, provider endpoint and API-key lookup in `build_model()` to the Groq values above. Set the environment variable matching the selected provider. Either provider can be used; only the selected provider's key is required. Setting a different key alone does not change an explicitly configured provider.

The commented model configurations are earlier experiments. Ollama is not required by the active configuration.

## Requirements

The supplied browser launcher and evaluation script target **Windows with PowerShell**.

- Python installed with the Windows `py` launcher. The setup example uses Python 3.12, matching the generated-code Docker image.
- Node.js and npm. The committed npm dependency lockfile requires Node.js 18 or newer.
- Docker Desktop running with Linux containers and the `docker` command available in PowerShell.
- A Gemini or Groq API key matching the configured provider, and internet access for model requests.

Python dependencies are listed in `requirements.txt`; their versions are not pinned. Model access and API limits depend on the provider.

## Setup

Open PowerShell in the project root: the folder containing `package.json`, `requirements.txt`, and `src`.

Create the virtual environment and install dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt openai
npm.cmd ci
```

Activation is unnecessary because these commands use the environment's interpreter directly. Keep the environment named `.venv`: the browser launcher specifically looks for `.venv\Scripts\python.exe`.

Start Docker Desktop, check that the engine is reachable, and download the execution image:

```powershell
docker info
docker pull python:3.12-slim
```

Set the API key in the same PowerShell session used to start the application. Replace the placeholder with your key.

For the default Gemini configuration:

```powershell
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

For a Groq-configured build:

```powershell
$env:GROQ_API_KEY = "YOUR_GROQ_API_KEY"
```

Set the console options:

```powershell
$env:PYTHONIOENCODING = "utf-8"
$env:NO_COLOR = "1"
```

These variables last for the current PowerShell session. The application does not automatically load a `.env` file.

## Browser interface

```powershell
node .\src\server.cjs
```

Open [http://localhost:3000](http://localhost:3000) or [http://127.0.0.1:3000](http://127.0.0.1:3000).

1. Select **Single agent** or **Multi-agent**.
2. Enter a task ID, such as `T01`, and a coding task.
3. Select **Run task** and inspect the output and final result.
4. Inspect or download generated `.py` files from **Workspace files**.

Example task:

```text
Create addition.py with add(a, b) returning a + b. Support positive, negative and zero integers. Use only Python's standard library. Write and run unittest tests.
```

The browser permits one active task at a time and displays the latest saved run. Its file list includes earlier runs. Keep the terminal open while using the interface; stop the server with `Ctrl+C`.

There is currently no `npm start` script. Use the explicit Node command above.

## Terminal usage

To run either mode with logging:

```powershell
.\.venv\Scripts\python.exe -u -B .\src\run_logged.py
```

Respond to the prompts with `single` or `multi` (lowercase), a task ID such as `T01`, and a coding task on one line.

To run an agent directly without the JSONL logging wrapper, choose one of these commands:

```powershell
# Single-agent baseline
.\.venv\Scripts\python.exe -u -B .\src\run_single_agent.py

# Multi-agent workflow
.\.venv\Scripts\python.exe -u -B .\src\run_multi_agent.py
```

Each direct runner prompts for a task.

## Files and logs

| Location | Contents |
| --- | --- |
| `runtime/workspace/` | Generated implementation files, shared across modes and runs. |
| `runtime/workspace/tests/` | Generated Python tests. |
| `runtime/logs/runs.jsonl` | Task ID, mode, task text, elapsed seconds, child exit code, and combined console output for each completed logger invocation. |
| `evaluation-results/` | Transcripts saved by the evaluation script. |

Runtime directories are created as needed. Agent tool paths are relative to `runtime/workspace/`: use `addition.py` or `tests/test_solution.py`, without a `workspace/` or `runtime/` prefix.

The logger merges standard error into `output`; its separate `errors` field is currently empty. The browser summary extracts fields from console text. Inspect the full output when summary information is missing.

## Execution and results

Generated `.py` files run in `python:3.12-slim` with a read-only workspace mount, no container network, a read-only root filesystem, a writable temporary directory, and CPU, memory, and process limits. The Docker command has a five-second timeout including startup. Pre-pulling the image avoids spending that timeout on an initial image download.

The agent application and Express server run on the host. Model requests need internet access; generated code has no container network access. The execution image has no project-specific third-party packages. Interactive programs, browser behaviour, PHP, and SQL database execution are outside the supported verification workflow. The browser lists only `.py` files.

| Multi-agent result | Meaning |
| --- | --- |
| `VERIFIED` | The Tester reports `PASS` and recorded executions meet the coordinator's checks: successful exit, a positive unittest count, and an `OK` line. |
| `UNVERIFIED` | The report or execution evidence does not establish a pass. |
| `FAILED after one repair.` | The Tester reports failure again after a repair. |
| `STOPPED` | A handled model/API error or worker step-limit condition prevents completion. |

For certain `400 tool_use_failed` errors, the coordinator can pass already-saved Coder files to the Tester or recover a Tester verdict from recorded passing executions. Recovery is identified in the output.

`VERIFIED` reflects the recorded checks, not proof of complete requirement coverage. The single-agent runner reports the agent's final answer without the coordinator's evidence checks.

**A zero process exit code does not prove that a task passed.** Handled failures can return normally, and the logger does not propagate a failed child's exit code to its own process. Inspect the final result and test output, including the number of tests run.

## Evaluation

`src/evaluation/tasks.txt` contains six standard-library Python tasks covering greeting, addition, subtraction, multiplication, parity, and character counting.

After setup and API-key configuration, run the supplied batch from the project root:

```powershell
.\src\evaluate.ps1
```

The script runs each task in single-agent mode followed by multi-agent mode: 12 runs in total. It saves transcripts such as `evaluation-results/E01-single.txt` and `evaluation-results/E01-multi.txt`; JSONL records are appended to `runtime/logs/runs.jsonl`. Re-running the batch overwrites transcripts with the same names. Each run makes model requests and is subject to provider limits.

**The batch does not reset the workspace or calculate a score.** Later runs can see earlier implementations and tests, so its output should not be presented as an isolated comparison.

For an independent manual comparison:

1. Use identical task text and model settings for both modes.
2. Before each individual run, archive any previous `runtime/workspace/` outside the active workspace. Start with an empty workspace; the tools recreate it as needed.
3. Run `src/run_logged.py` with the selected mode and task ID.
4. Preserve the implementation, tests, full output, final result, test count, elapsed time, and any API or execution failure.
5. Repeat for the other mode with a fresh workspace. Review test quality against the original requirements as well as the reported outcome.

The supplied transcripts include successful, stopped and recovered runs. Historical Groq results and later Gemini results should be identified separately; results from different models do not provide an architecture-only comparison. No aggregate comparison results are included.

## Project layout

```text
public/index.html              Browser interface
src/server.cjs                 Express server and Python launcher
src/run_single_agent.py        Single-agent entry point
src/run_multi_agent.py         Multi-agent entry point
src/run_logged.py              Console streaming and JSONL logging
src/agents/agent_setup.py      Model and agent construction
src/agents/agent_prompts.py    Role and testing instructions
src/agents/coordinator.py      Coder/Tester workflow and evidence checks
src/tools/agent_toolsets.py    Tools available to each role
src/tools/file_manager.py      Workspace file operations
src/tools/test_manager.py      Test-file writing tool
src/tools/code_executor.py     Docker execution tool
src/evaluate.ps1               Batch evaluation runner
src/evaluation/tasks.txt       Evaluation task definitions
requirements.txt              Python dependencies
package.json                  Node.js dependencies
package-lock.json             Locked npm dependency tree
```

## Troubleshooting and limitations

| Symptom | Check or action |
| --- | --- |
| `Invalid origin.` | Open `http://localhost:3000` or `http://127.0.0.1:3000`. |
| Missing key or API-key `KeyError` | Set the environment variable required by `build_model()` before starting Node or Python. Restart Node if the key was set afterward. |
| `Could not start Python` | Create `.venv` in the project root and install its dependencies. |
| Docker unavailable or execution times out | Start Docker Desktop with Linux containers, check `docker info`, and pre-pull `python:3.12-slim`. |
| Model/API or tool-call error | Inspect the full output and provider response; saved files alone do not establish success. |
| Unexpected files from an earlier task | Archive the previous workspace and start the next run with an empty one. |

The Coder's restriction against editing test files is prompt-based; its general file tools do not enforce that role boundary. Test evidence is checked from recorded output rather than tied to immutable file versions.

The project has no automated regression suite for the assistant itself, and `npm test` is a placeholder that exits with an error. Generated task tests are separate from tests of the assistant application.