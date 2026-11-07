const express = require("express");
const { spawn } = require("node:child_process");
const path = require("node:path");
const fs = require("node:fs");

const app = express();
const project = path.resolve(__dirname, "..");  
const workspace = path.join(project, "runtime", "workspace");
const python = path.join(project, ".venv", "Scripts", "python.exe");

let running = false;

app.use(express.json());
app.use(express.static(path.join(project, "public")));

app.post("/run", (req, res) => {
    // Only accept browser requests from our local page.
    const origin = req.get("origin");
    if (origin && ![
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ].includes(origin)) {
        return res.status(403).send("Invalid origin.");
    }

    if (running) {
        return res.status(409).send("Another task is already running.");
    }

    const mode = req.body.mode;
    const task = String(req.body.task || "").replace(/[\r\n]+/g, " ").trim();
    const taskId = String(req.body.taskId || "GUI").replace(/[\r\n]+/g, " ");

    if (!["single", "multi"].includes(mode) || !task) {
        return res.status(400).send("Choose a system and enter a task.");
    }

    if (!process.env.GROQ_API_KEY || !process.env.GEMINI_API_KEY) {
        return res.status(400).send("Set API_KEY before starting Node.");
    }


    running = true;
    res.type("text/plain; charset=utf-8");
    res.write("Starting Python...\n");

    const child = spawn(
        python,
        ["-u", "-B", path.join(project, "src", "run_logged.py")],
        {
            cwd: project,
            windowsHide: true,
            env: {
                ...process.env,
                PYTHONIOENCODING: "utf-8",
                NO_COLOR: "1"
            }
        }
    );

    function send(text) {
        if (!res.destroyed) {
            res.write(text);
        }
    }

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");

    child.stdout.on("data", send);
    child.stderr.on("data", send);

    child.on("error", error => {
        send("\nCould not start Python: " + error.message);
    });

    child.on("close", code => {
        running = false;
        if (!res.destroyed) {
            res.end("\nLogger finished. Exit code: " + code);
        }
    });

    // Answer the existing logger's three input prompts.
    child.stdin.on("error", () => {});
    child.stdin.end(`${mode}\n${taskId}\n${task}\n`);
});

// List Python files without following directory links.
function findFiles(folder, prefix = "") {
    if (!fs.existsSync(folder)) return [];

    return fs.readdirSync(folder, { withFileTypes: true }).flatMap(item => {
        const name = prefix + item.name;

        if (item.isDirectory()) {
            return findFiles(path.join(folder, item.name), name + "/");
        }

        return item.isFile() && name.toLowerCase().endsWith(".py") ? [name] : [];
    });
}

app.get("/files", (req, res) => {
    res.json(findFiles(workspace));
});

app.get("/file", (req, res) => {
    try {
        const root = fs.realpathSync(workspace);
        const file = fs.realpathSync(
            path.resolve(root, String(req.query.name || ""))
        );
        const relative = path.relative(root, file);

        if (
            relative.startsWith(".." + path.sep) ||
            relative === ".." ||
            path.isAbsolute(relative) ||
            !fs.statSync(file).isFile() ||
            !file.toLowerCase().endsWith(".py")
        ) {
            return res.status(403).send("Invalid file.");
        }

        res.type("text/plain").sendFile(file);
    } catch {
        res.status(404).send("File not found.");
    }
});

app.get("/latest-log", (req, res) => {
    try {
        const text = fs.readFileSync(
            path.join(project, "runtime", "logs", "runs.jsonl"), "utf8"
        );
        const lines = text.trim().split(/\r?\n/);
        res.json(JSON.parse(lines[lines.length - 1]));
    } catch {
        res.sendStatus(404);
    }
});

app.listen(3000, "127.0.0.1", () => {
    console.log("Open http://127.0.0.1:3000");
});


