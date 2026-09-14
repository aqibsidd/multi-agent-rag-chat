// One command: `pm2 start ecosystem.config.js`
// Starts FastAPI backend (:8000) + Vite frontend (:5173) together.
// Vite already proxies /ingest, /chat, /health -> localhost:8000 (see frontend/vite.config.js).
// Prereqs running separately: `ollama serve` and `docker compose up -d` (Qdrant).
// NOTE: absolute paths below — PM2 resolves `script` from its own cwd,
// and the venv's uvicorn shebang hardcodes the old absolute path, so the
// backend runs via `venv/python -m uvicorn` instead.
const path = require("path");
const ROOT = __dirname;

module.exports = {
  apps: [
    {
      name: "rag-backend",
      cwd: path.join(ROOT, "backend"),
      script: path.join(ROOT, "backend", ".venv", "bin", "python"),
      args: "-m uvicorn app.main:app --host 0.0.0.0 --port 8000",
      exec_mode: "fork",
      interpreter: "none",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      env: {
        PORT: "8000",
      },
    },
    {
      name: "rag-frontend",
      cwd: path.join(ROOT, "frontend"),
      script: "npm",
      args: "run dev -- --host --port 5173",
      exec_mode: "fork",
      interpreter: "none",
      autorestart: true,
      watch: false,
      max_restarts: 10,
    },
  ],
};
