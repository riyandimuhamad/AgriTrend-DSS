#!/usr/bin/env node

const { execSync, spawn } = require("child_process");
const { existsSync, copyFileSync } = require("fs");
const { join } = require("path");

const ROOT = __dirname;
const FRONTEND_DIR = join(ROOT, "frontend");
const BACKEND_DIR = join(ROOT, "backend");

const c = {
  reset: "\x1b[0m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  red: "\x1b[31m",
  cyan: "\x1b[36m",
  bold: "\x1b[1m",
  dim: "\x1b[2m",
};

function log(msg, color = "reset") {
  console.log(`${c[color]}${msg}${c.reset}`);
}

function run(cmd, cwd = ROOT) {
  log(`  > ${cmd}`, "dim");
  execSync(cmd, { cwd, stdio: "inherit" });
}

function checkNode() {
  const version = process.versions.node.split(".").map(Number);
  if (version[0] < 24) {
    log(
      `\n[ERROR] Node.js v24+ diperlukan. Versi kamu: v${process.versions.node}`,
      "red",
    );
    log("        Download: https://nodejs.org/en/download\n", "yellow");
    process.exit(1);
  }
  log(`[ok] Node.js v${process.versions.node}`, "green");
}

function hasUv() {
  try {
    execSync("uv --version", { stdio: "pipe" });
    return true;
  } catch {
    return false;
  }
}

function setupEnvFiles() {
  log("\n-- Menyiapkan file .env --", "bold");

  const backendEnv = join(BACKEND_DIR, ".env");
  const backendEnvExample = join(BACKEND_DIR, ".env.example");
  if (!existsSync(backendEnv) && existsSync(backendEnvExample)) {
    copyFileSync(backendEnvExample, backendEnv);
    log("[ok] backend/.env dibuat dari .env.example", "green");
    log(
      "[!]  Isi SUPABASE_URL, SUPABASE_KEY, dan GEMINI_API_KEY di backend/.env",
      "yellow",
    );
  } else if (existsSync(backendEnv)) {
    log("[ok] backend/.env sudah ada", "green");
  }

  const frontendEnv = join(FRONTEND_DIR, ".env");
  const frontendEnvExample = join(FRONTEND_DIR, ".env.example");
  if (!existsSync(frontendEnv) && existsSync(frontendEnvExample)) {
    copyFileSync(frontendEnvExample, frontendEnv);
    log("[ok] frontend/.env dibuat dari .env.example", "green");
  } else if (existsSync(frontendEnv)) {
    log("[ok] frontend/.env sudah ada", "green");
  }
}

function installFrontend() {
  log("\n-- Install dependencies frontend --", "bold");
  run("npm install", FRONTEND_DIR);
  log("[ok] Frontend dependencies terinstall", "green");
}

function installBackend() {
  log("\n-- Install dependencies backend (Python) --", "bold");
  if (hasUv()) {
    log("[ok] uv ditemukan", "green");
    run("uv sync", BACKEND_DIR);
  } else {
    log("[!]  uv tidak ditemukan, menggunakan pip", "yellow");
    run("pip install -r requirements.txt", BACKEND_DIR);
  }
  log("[ok] Backend dependencies terinstall", "green");
}

function setupMLModels() {
  log("\n-- Menyiapkan model Machine Learning --", "bold");
  const ML_DIR = join(ROOT, "ml_models");
  const isWin = process.platform === "win32";
  const venvPython = isWin
    ? join(BACKEND_DIR, ".venv", "Scripts", "python.exe")
    : join(BACKEND_DIR, ".venv", "bin", "python");

  let pythonCmd = "python";
  if (existsSync(venvPython)) {
    pythonCmd = venvPython;
    log(`[ok] Virtual environment python ditemukan: ${venvPython}`, "green");
  } else {
    try {
      execSync("python3 --version", { stdio: "pipe" });
      pythonCmd = "python3";
    } catch {
      pythonCmd = "python";
    }
    log(`[!]  Virtual environment tidak ditemukan. Menggunakan system python: ${pythonCmd}`, "yellow");
  }

  log("\nRunning train_model.py...");
  run(`"${pythonCmd}" train_model.py`, ML_DIR);
  log("[ok] train_model.py selesai dijalankan", "green");

  log("\nRunning predictor.py...");
  run(`"${pythonCmd}" predictor.py`, ML_DIR);
  log("[ok] predictor.py selesai dijalankan", "green");
}

function startDev() {
  log("\n-- Menjalankan development server --", "bold");
  log("     Backend  -> http://localhost:8000", "cyan");
  log("     Frontend -> http://localhost:5173\n", "cyan");

  const useUv = hasUv();
  const backendArgs = useUv
    ? [
        "uv",
        [
          "run",
          "uvicorn",
          "app.main:app",
          "--reload",
          "--host",
          "0.0.0.0",
          "--port",
          "8000",
        ],
      ]
    : [
        "uvicorn",
        ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
      ];

  const backend = spawn(backendArgs[0], backendArgs[1], {
    cwd: BACKEND_DIR,
    stdio: "inherit",
    shell: process.platform === "win32",
  });

  const frontend = spawn("npm", ["run", "dev"], {
    cwd: FRONTEND_DIR,
    stdio: "inherit",
    shell: process.platform === "win32",
  });

  const cleanup = () => {
    backend.kill();
    frontend.kill();
    process.exit(0);
  };

  process.on("SIGINT", cleanup);
  process.on("SIGTERM", cleanup);

  backend.on("exit", (code) => {
    if (code !== 0 && code !== null)
      log(`[ERROR] Backend berhenti dengan kode ${code}`, "red");
  });
  frontend.on("exit", (code) => {
    if (code !== 0 && code !== null)
      log(`[ERROR] Frontend berhenti dengan kode ${code}`, "red");
  });
}

// --- Main ---
const command = process.argv[2] || "all";

log("\n\uD83C\uDF3E AgriTrend-DSS Setup", "bold");
log("======================\n");

checkNode();

switch (command) {
  case "install":
    setupEnvFiles();
    installFrontend();
    installBackend();
    setupMLModels();
    log(
      "\n\uD83C\uDF31 Instalasi selesai. Jalankan: node setup.js dev\n",
      "green",
    );
    break;

  case "dev":
    startDev();
    break;

  case "all":
  default:
    setupEnvFiles();
    installFrontend();
    installBackend();
    setupMLModels();
    log("\n\uD83C\uDF31 Instalasi selesai. Memulai server...\n", "green");
    startDev();
    break;
}
