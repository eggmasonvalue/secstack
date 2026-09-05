#!/usr/bin/env node
/**
 * Install SecStack and its independently managed Pi packages into the isolated
 * SecStack profile.
 *
 * This script deliberately changes only the SecStack profile's package list,
 * shell command prefix, and optional Bash launcher.
 */
import { execFileSync } from "node:child_process";
import {
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readlinkSync,
  renameSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
import { homedir } from "node:os";
import { dirname, join, relative, resolve } from "node:path";

const agentDir = resolve(join(homedir(), ".pi", "secstack-agent"));
const settingsPath = join(agentDir, "settings.json");
const npmBin = join(agentDir, "npm", "node_modules", ".bin");
const venvDir = join(agentDir, ".venv");
const systemPromptPath = join(agentDir, "SYSTEM.md");
const bashrcPath = join(homedir(), ".bashrc");
const secstackSource = "git:github.com/eggmasonvalue/secstack";
const piSetupSource = "git:github.com/eggmasonvalue/pi-setup";
const systemPromptViewerSource =
  "git:github.com/eggmasonvalue/pi-system-prompt-viewer";
const agentBrowserSource = "npm:agent-browser";

const managedSources = [
  secstackSource,
  piSetupSource,
  systemPromptViewerSource,
  agentBrowserSource,
];

const desiredPackages = [
  secstackSource,
  systemPromptViewerSource,
  {
    source: piSetupSource,
    extensions: [
      "extensions/btw.ts",
      "extensions/notify.ts",
      "extensions/session-context.ts",
      "extensions/tavily-web.ts",
      "extensions/vibe-spinner.ts",
    ],
    skills: [],
    prompts: [],
    themes: [
      "themes/midnight-pastel.json",
      "themes/pastel-dark.json",
      "themes/pastel-light.json",
    ],
  },
  agentBrowserSource,
];

const managedPathMarker = ".pi/secstack-agent";
const launcherStart = "# >>> secpi launcher >>>";
const launcherEnd = "# <<< secpi launcher <<<";

function sourceOf(entry) {
  return typeof entry === "string" ? entry : entry?.source;
}

function run(command, args, env = {}) {
  console.log(`\n> ${command} ${args.join(" ")}`);
  execFileSync(command, args, {
    stdio: "inherit",
    shell: process.platform === "win32",
    env: {
      ...process.env,
      ...env,
    },
  });
}

function runPi(args, env = {}) {
  run("pi", args, {
    PI_CODING_AGENT_DIR: agentDir,
    ...env,
  });
}

function commandWorks(command, args) {
  try {
    execFileSync(command, args, {
      stdio: "ignore",
      shell: process.platform === "win32",
    });
    return true;
  } catch {
    return false;
  }
}

function findUv() {
  if (commandWorks("uv", ["--version"])) return "uv";
  throw new Error(
    "uv was not found. Install uv and ensure it is on PATH, then rerun bootstrap.",
  );
}

function installedSecStackPath(...parts) {
  return join(
    agentDir,
    "git",
    "github.com",
    "eggmasonvalue",
    "secstack",
    ...parts,
  );
}

function mergeSettings() {
  mkdirSync(agentDir, { recursive: true });
  let settings = {};
  if (existsSync(settingsPath)) {
    settings = JSON.parse(readFileSync(settingsPath, "utf8"));
  }

  const existing = Array.isArray(settings.packages) ? settings.packages : [];
  const managed = new Set(managedSources);
  settings.packages = [
    ...existing.filter((entry) => !managed.has(sourceOf(entry))),
    ...desiredPackages,
  ];

  // Pi evaluates shellCommandPrefix inside Bash. Add both virtualenv layouts;
  // the non-existent layout is harmless and this works in Git Bash on Windows
  // as well as Bash on macOS/Linux.
  const pathCommand =
    'export PATH="$HOME/.pi/secstack-agent/.venv/Scripts:$HOME/.pi/secstack-agent/.venv/bin:$HOME/.pi/secstack-agent/npm/node_modules/.bin:$PATH"';
  const prefix =
    typeof settings.shellCommandPrefix === "string"
      ? settings.shellCommandPrefix
      : "";
  if (!prefix.includes(managedPathMarker)) {
    settings.shellCommandPrefix = prefix
      ? `${prefix}\n${pathCommand}`
      : pathCommand;
  }

  const temp = join(agentDir, `.settings.${process.pid}.tmp`);
  writeFileSync(temp, `${JSON.stringify(settings, null, 2)}\n`, "utf8");
  renameSync(temp, settingsPath);
}

function ensurePythonEnvironment() {
  const uv = findUv();
  const projects = [
    installedSecStackPath("skills", "signal-sweep"),
    installedSecStackPath("skills", "sec-edgar-skill"),
    installedSecStackPath("skills", "market-scout"),
  ];
  for (const project of projects) {
    const pyproject = join(project, "pyproject.toml");
    const lockfile = join(project, "uv.lock");
    for (const file of [pyproject, lockfile]) {
      if (!existsSync(file)) {
        throw new Error(`Installed SecStack package is missing ${file}`);
      }
    }
    // Each skill owns its dependency graph. Keep prior skills' packages in the
    // shared profile environment while syncing the next one.
    run(
      uv,
      [
        "sync",
        "--project",
        project,
        "--no-dev",
        "--inexact",
        "--locked",
      ],
      { UV_PROJECT_ENVIRONMENT: venvDir },
    );
  }
}

function linkSystemPrompt() {
  const installed = installedSecStackPath("SYSTEM.md");
  if (!existsSync(installed)) {
    throw new Error(
      `Installed SecStack package is missing SYSTEM.md: ${installed}`,
    );
  }

  const target = relative(agentDir, installed);
  try {
    if (lstatSync(systemPromptPath).isSymbolicLink()) {
      if (readlinkSync(systemPromptPath) === target) return;
      rmSync(systemPromptPath, { force: true });
    } else {
      const backup = `${systemPromptPath}.local-backup`;
      if (existsSync(backup)) {
        throw new Error(
          `A regular ${systemPromptPath} and its backup ${backup} already exist; refusing to overwrite either file.`,
        );
      }
      renameSync(systemPromptPath, backup);
      console.warn(`Preserved the previous regular file as ${backup}`);
    }
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
  }

  try {
    symlinkSync(target, systemPromptPath, "file");
    console.log(`Linked ${systemPromptPath} -> ${target}`);
  } catch (error) {
    throw new Error(
      `Could not create the SYSTEM.md symlink. Enable Windows Developer Mode or grant symlink privileges, then rerun bootstrap. Original error: ${error.message}`,
    );
  }
}

function launcherBlock() {
  return `${launcherStart}
secpi() {
  local agent_dir="$HOME/.pi/secstack-agent"
  local venv="$agent_dir/.venv"

  if [ -f "$venv/Scripts/activate" ]; then
    . "$venv/Scripts/activate"
  elif [ -f "$venv/bin/activate" ]; then
    . "$venv/bin/activate"
  fi

  export PATH="$venv/Scripts:$venv/bin:$agent_dir/npm/node_modules/.bin:$PATH"
  PI_CODING_AGENT_DIR="$agent_dir" pi "$@"
}
${launcherEnd}`;
}

function installLauncher() {
  mkdirSync(dirname(bashrcPath), { recursive: true });
  const existing = existsSync(bashrcPath)
    ? readFileSync(bashrcPath, "utf8")
    : "";
  const block = launcherBlock();
  const pattern = new RegExp(
    `${escapeRegExp(launcherStart)}[\\s\\S]*?${escapeRegExp(launcherEnd)}\\n?`,
  );
  const content = pattern.test(existing)
    ? existing.replace(pattern, `${block}\n`)
    : `${existing.trimEnd()}${existing ? "\n\n" : ""}${block}\n`;
  const temp = `${bashrcPath}.${process.pid}.tmp`;
  writeFileSync(temp, content, "utf8");
  renameSync(temp, bashrcPath);
  console.log(`Added the secpi launcher to ${bashrcPath}`);
  console.log("Open a new Bash shell, or run: source ~/.bashrc");
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\[\]\\]/g, "\\$&");
}

async function offerLauncher() {
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    console.log(
      `Launcher not offered because bootstrap is not running in an interactive Bash terminal.`,
    );
    return;
  }

  const rl = createInterface({ input, output });
  try {
    const answer = (
      await rl.question("Create the secpi Bash launcher? [Y/n] ")
    )
      .trim()
      .toLowerCase();
    if (answer === "" || answer === "y" || answer === "yes") {
      installLauncher();
    } else {
      console.log("Skipped the secpi launcher.");
    }
  } finally {
    rl.close();
  }
}

async function main() {
  console.log(`Configuring SecStack Pi under ${agentDir}`);
  for (const source of managedSources) {
    runPi(["install", source]);
  }
  mergeSettings();
  linkSystemPrompt();
  mkdirSync(npmBin, { recursive: true });
  ensurePythonEnvironment();
  await offerLauncher();

  console.log("\nSecStack Pi bootstrap complete.");
  console.log("Update everything Pi-managed with:");
  console.log("  secpi update --extensions");
  console.log(
    "One-time browser setup (if not already done): agent-browser install",
  );
  console.log("Verify from the SecStack profile: agent-browser --version");
}

try {
  await main();
} catch (error) {
  console.error(`\nBootstrap failed: ${error.message}`);
  process.exitCode = 1;
}
