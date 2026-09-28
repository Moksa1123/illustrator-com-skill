#!/usr/bin/env node
/**
 * illustrator-com — install the Illustrator COM skill into 14 AI coding assistants and keep it up to date.
 *
 *   npx illustrator-com-skill init --ai claude -g     # runtime -> ~/.illustrator-com-skill, SKILL.md -> ~/.claude/skills/illustrator-com
 *   illustrator-com init --ai all                     # every platform, project scope (current folder)
 *   illustrator-com setup                             # pip install -r requirements.txt, build the API index, doctor
 *   illustrator-com doctor [--smoke]                  # Windows / Python / packages / Illustrator COM / index
 *   illustrator-com update                            # latest version from npm -> runtime + every recorded install
 *   illustrator-com check [--quiet]                   # update check (cached 24 h); runs update when auto-update is on
 *   illustrator-com config auto-update on|off
 *   illustrator-com list | info | versions | status | sync | uninstall
 *
 * One runtime (lib/, tools/, index/, tests/, presets/) lives in the skill home; every platform gets a SKILL.md that
 * points at it, so the per-machine API index (index/ai-dom.json, built from YOUR Illustrator) is built once and
 * survives updates. Zero dependencies: Node 18+ stdlib only.
 */
import { readFileSync, writeFileSync, existsSync, mkdirSync, readdirSync, lstatSync, copyFileSync,
  rmSync, rmdirSync, unlinkSync, symlinkSync, realpathSync } from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir, platform as osPlatform } from "node:os";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import { createInterface } from "node:readline/promises";

const PKG_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const PKG = JSON.parse(readFileSync(join(PKG_ROOT, "package.json"), "utf8"));
const NAME = PKG.name;                                   // illustrator-com-skill
const SKILL = "illustrator-com";
const PLATFORMS_DIR = join(PKG_ROOT, "assets", "templates", "platforms");
const SKILL_HOME = resolve(process.env.ILLUSTRATOR_COM_SKILL_HOME || join(homedir(), ".illustrator-com-skill"));
const STATE_DIR = join(SKILL_HOME, "_state");
const STATE_FILE = join(STATE_DIR, "state.json");
const REGISTRY = `https://registry.npmjs.org/${NAME}`;
const MARK = "<!-- installed by illustrator-com-skill: `illustrator-com update` rewrites this file -->";

// Never copied into the runtime (repo-only or generated per machine) and never touched there by sync.
const EXCLUDE_DIRS = new Set([".git", "node_modules", "__pycache__", "_state", ".claude", ".github"]);
const EXCLUDE_REL = ["index/ai-dom.json", "index/raw", "tests/snaps", "tests/fixtures/fixture", "tests/fixtures/out", "examples/out"];
const EXCLUDE_EXT = [".pyc", ".log", ".tgz"];

const out = (s = "") => process.stdout.write(s + "\n");
const err = (s) => process.stderr.write(s + "\n");
const expand = (p) => (p && p.startsWith("~") ? join(homedir(), p.slice(1)) : p);
const sha1 = (f) => createHash("sha1").update(readFileSync(f)).digest("hex");
const posix = (p) => p.split(sep).join("/");

// ---------- state ------------------------------------------------------------------------------------------------

function loadState() {
  try { return JSON.parse(readFileSync(STATE_FILE, "utf8")); } catch { return { installs: [], config: { autoUpdate: false, checkHours: 24 } }; }
}
function saveState(s) {
  mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(s, null, 2) + "\n", "utf8");
}

// ---------- platforms ----------------------------------------------------------------------------------------------

function platforms() {
  return readdirSync(PLATFORMS_DIR).filter((f) => f.endsWith(".json")).sort()
    .map((f) => JSON.parse(readFileSync(join(PLATFORMS_DIR, f), "utf8")));
}
function platform(key) {
  const p = platforms().find((x) => x.platform === key);
  if (!p) throw new Error(`Unknown platform "${key}". Run: illustrator-com list`);
  return p;
}

// ---------- runtime (skill home) -----------------------------------------------------------------------------------

function isLink(p) { try { return lstatSync(p).isSymbolicLink(); } catch { return false; } }
function sameDir(a, b) { try { return realpathSync(a).toLowerCase() === realpathSync(b).toLowerCase(); } catch { return false; } }

function runtimeFiles(root) {
  const files = [];
  const walk = (dir) => {
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      const full = join(dir, e.name);
      const rel = posix(relative(root, full));
      if (EXCLUDE_REL.some((x) => rel === x || rel.startsWith(x + "/"))) continue;
      if (e.isDirectory()) { if (!EXCLUDE_DIRS.has(e.name)) walk(full); continue; }
      if (EXCLUDE_EXT.some((x) => e.name.endsWith(x))) continue;
      files.push(rel);
    }
  };
  walk(root);
  return files.sort();
}

/** Copy this package into the skill home. Files the user edited there are backed up first; generated files the
 *  package does not ship (index/ai-dom.json, index/raw/, test snapshots) are never touched. */
function syncRuntime(state, { dryRun = false } = {}) {
  if (existsSync(SKILL_HOME) && sameDir(SKILL_HOME, PKG_ROOT)) return { linked: true, copied: 0, removed: 0, backedUp: 0 };
  if (isLink(SKILL_HOME)) {                                // was --link'ed to a checkout: replace the link, not its target
    if (!dryRun) unlinkSync(SKILL_HOME);
  }
  const prev = state.manifest || {};
  const files = runtimeFiles(PKG_ROOT);
  const manifest = {};
  let copied = 0, removed = 0, backedUp = 0;
  const backupDir = join(STATE_DIR, "backup", `${state.version || "unknown"}-${Date.now()}`);
  const backup = (rel) => {
    const dst = join(backupDir, rel);
    if (!dryRun) { mkdirSync(dirname(dst), { recursive: true }); copyFileSync(join(SKILL_HOME, rel), dst); }
    backedUp++;
  };
  for (const rel of files) {
    const src = join(PKG_ROOT, rel), dst = join(SKILL_HOME, rel);
    const h = sha1(src);
    manifest[rel] = h;
    if (existsSync(dst)) {
      const cur = sha1(dst);
      if (cur === h) continue;
      if (prev[rel] && cur !== prev[rel]) backup(rel);     // edited locally since the last sync
    }
    if (!dryRun) { mkdirSync(dirname(dst), { recursive: true }); copyFileSync(src, dst); }
    copied++;
  }
  for (const rel of Object.keys(prev)) {                   // dropped from the package since the last sync
    if (manifest[rel]) continue;
    const dst = join(SKILL_HOME, rel);
    if (!existsSync(dst)) continue;
    if (sha1(dst) !== prev[rel]) backup(rel);
    if (!dryRun) unlinkSync(dst);
    removed++;
  }
  if (!dryRun) { state.manifest = manifest; state.version = PKG.version; state.linked = false; }
  return { linked: false, copied, removed, backedUp, backupDir: backedUp ? backupDir : null };
}

function linkRuntime(state, force) {
  if (sameDir(SKILL_HOME, PKG_ROOT)) return;
  if (existsSync(SKILL_HOME) || isLink(SKILL_HOME)) {
    if (isLink(SKILL_HOME)) unlinkSync(SKILL_HOME);
    else if (!force) throw new Error(`${SKILL_HOME} already holds a copied runtime (and maybe your API index). `
      + `Move index/ai-dom.json into ${PKG_ROOT}\\index if you want to keep it, then re-run with --force.`);
    else {
      const idx = join(SKILL_HOME, "index", "ai-dom.json");
      const keep = join(PKG_ROOT, "index", "ai-dom.json");
      if (existsSync(idx) && !existsSync(keep)) copyFileSync(idx, keep);
      rmSync(SKILL_HOME, { recursive: true, force: true });
    }
  }
  mkdirSync(dirname(SKILL_HOME), { recursive: true });
  symlinkSync(PKG_ROOT, SKILL_HOME, "junction");           // no admin rights needed for a junction
  state.linked = true; state.version = PKG.version; state.manifest = {};
}

// ---------- SKILL.md adapter ---------------------------------------------------------------------------------------

function skillSource() {
  const raw = readFileSync(join(PKG_ROOT, "SKILL.md"), "utf8").replace(/\r\n/g, "\n");
  const m = raw.match(/^---\n([\s\S]*?)\n---\n+/);
  const fm = {};
  if (m) for (const line of m[1].split("\n")) {
    const i = line.indexOf(":");
    if (i > 0) fm[line.slice(0, i).trim()] = line.slice(i + 1).trim();
  }
  return { fm, body: m ? raw.slice(m[0].length) : raw };
}

function yamlValue(v) { if (typeof v === "boolean" || typeof v === "number") return String(v); return /^[\w.\- ]+$/.test(String(v)) && !/^(true|false|yes|no|null)$/i.test(String(v)) ? String(v) : JSON.stringify(String(v)); }

function renderSkill(cfg, state) {
  const { fm, body } = skillSource();
  const home = SKILL_HOME;
  const py = state.python?.exe || "python";
  const front = { name: fm.name || SKILL, description: fm.description, version: PKG.version, ...cfg.frontmatter };
  const lines = ["---", ...Object.entries(front).filter(([, v]) => v != null).map(([k, v]) => `${k}: ${k === "description" ? v : yamlValue(v)}`), "---", ""];
  const where = [
    MARK,
    `> **Runtime location.** Every path in this skill (\`lib/\`, \`tools/\`, \`index/\`, \`tests/\`, \`presets/\`) is relative to`,
    `> \`${home}\`. Run commands from there, e.g. \`cd "${home}" && "${py}" index/ai_api.py find text frame\`.`,
    `> Skill ${PKG.version} for ${cfg.displayName}. Once per session run \`node "${join(home, "bin", "illustrator-com.mjs")}" check --quiet\`:`,
    `> it prints one line only when a newer version exists (and installs it when auto-update is on).`,
    "", "",
  ];
  const fixed = body.replace('sys.path.insert(0, "lib")', `sys.path.insert(0, r"${join(home, "lib")}")`);
  return lines.join("\n") + where.join("\n") + fixed;
}

function targetFor(cfg, { global: g, to }) {
  const fs_ = cfg.folderStructure;
  if (to) return join(resolve(expand(to)), fs_.skillPath, fs_.filename);
  if (g) {
    if (!fs_.globalRoot) return null;
    return join(expand(fs_.globalRoot), fs_.globalSkillPath || fs_.skillPath, fs_.filename);
  }
  return join(process.cwd(), fs_.root, fs_.skillPath, fs_.filename);
}

function writeAdapter(inst, state, { force = true, dryRun = false } = {}) {
  const cfg = platform(inst.platform);
  const content = renderSkill(cfg, state);
  if (dryRun) return content.length;
  if (existsSync(inst.file) && !force && !readFileSync(inst.file, "utf8").includes(MARK))
    throw new Error(`${inst.file} exists and was not written by this installer (use --force to replace it).`);
  mkdirSync(dirname(inst.file), { recursive: true });
  writeFileSync(inst.file, content, "utf8");
  return content.length;
}

// ---------- python / doctor ----------------------------------------------------------------------------------------

function findPython() {
  for (const cmd of [["py", "-3"], ["python"], ["python3"]]) {
    const r = spawnSync(cmd[0], [...cmd.slice(1), "-c", "import sys;print(sys.executable);print('%d.%d'%sys.version_info[:2])"], { encoding: "utf8" });
    if (r.status === 0 && r.stdout.trim()) {
      const [exe, ver] = r.stdout.trim().split(/\r?\n/);
      if (exe && !exe.includes("WindowsApps")) return { exe, version: ver };
    }
  }
  return null;
}

function regHas(key) { return spawnSync("reg", ["query", key], { stdio: "ignore" }).status === 0; }

const MODULES = [
  ["win32com.client", "pywin32", true], ["psutil", "psutil", true], ["PIL", "Pillow", true], ["pywinauto", "pywinauto", true],
  ["pypdf", "pypdf", false, "logo_package PDF checks"], ["docx", "python-docx", false, "md_docx / tipo_form"],
  ["playwright", "playwright", false, "html2ai"],
];

function doctor(state, { smoke = false } = {}) {
  let bad = 0;
  const row = (ok, label, hint = "") => { out(`  ${ok === true ? "✓" : ok === false ? "✗" : "!"} ${label}${hint ? "  — " + hint : ""}`); if (ok === false) bad++; };
  out(`illustrator-com-skill ${PKG.version}   home: ${SKILL_HOME}${state.linked ? " (linked to checkout)" : ""}`);
  row(osPlatform() === "win32", `Windows (${osPlatform()})`, osPlatform() === "win32" ? "" : "Illustrator COM needs Windows");
  row(Number(process.versions.node.split(".")[0]) >= 18, `Node ${process.versions.node}`);
  const home = existsSync(join(SKILL_HOME, "lib", "ai_run.py"));
  row(home, "runtime installed", home ? "" : "run: illustrator-com init --ai <platform>");
  const py = findPython();
  if (py) { state.python = py; saveState(state); }
  const pyOk = py && Number(py.version.split(".")[1]) >= 9;
  row(!!pyOk, `Python ${py ? py.version + "  " + py.exe : "not found"}`, pyOk ? "" : "install Python 3.9+ from python.org");
  if (py) {
    const code = MODULES.map(([m]) => `\ntry:\n import ${m}\n print('${m}',1)\nexcept Exception:\n print('${m}',0)`).join("");
    const r = spawnSync(py.exe, ["-c", code], { encoding: "utf8" });
    const got = Object.fromEntries((r.stdout || "").trim().split(/\r?\n/).map((l) => l.split(" ")));
    for (const [m, pkg, req, why] of MODULES) {
      const ok = got[m] === "1";
      row(ok ? true : req ? false : "warn", `${pkg}${req ? "" : ` (optional: ${why})`}`, ok ? "" : "run: illustrator-com setup");
    }
  }
  const ai = regHas("HKCR\\Illustrator.Application");
  row(ai, "Illustrator COM registered (Illustrator.Application)", ai ? "" : "install Adobe Illustrator and start it once");
  row(regHas("HKCR\\Word.Application") ? true : "warn", "Microsoft Word COM (optional: DOCX -> PDF)");
  const idx = existsSync(join(SKILL_HOME, "index", "ai-dom.json"));
  row(idx ? true : "warn", "API index built from your Illustrator (index/ai-dom.json)", idx ? "" : "run: illustrator-com setup (starts Illustrator)");
  if (smoke && home && py && ai) {
    const r = spawnSync(py.exe, ["-c", "import sys;sys.path.insert(0,'lib');from ai_run import run_js;print(run_js('app.name+\" \"+app.version'))"],
      { cwd: SKILL_HOME, encoding: "utf8", timeout: 180000 });
    const ok = r.status === 0 && /Illustrator/i.test(r.stdout);
    row(ok, `smoke test: ${ok ? r.stdout.trim() : (r.stderr || r.stdout || "timeout").trim().split("\n").pop()}`);
  }
  out(bad ? `\n${bad} problem(s).` : "\nAll required checks passed.");
  return bad ? 1 : 0;
}

function setup(state, { playwright = false, index = true } = {}) {
  const py = findPython();
  if (!py) { err("Python 3.9+ not found. Install it from python.org (tick 'Add to PATH'), then re-run."); return 1; }
  state.python = py; saveState(state);
  if (!existsSync(join(SKILL_HOME, "lib", "ai_run.py"))) { syncRuntime(state); saveState(state); }
  out(`> ${py.exe} -m pip install -r requirements.txt`);
  let r = spawnSync(py.exe, ["-m", "pip", "install", "-r", "requirements.txt"], { cwd: SKILL_HOME, stdio: "inherit" });
  if (r.status !== 0) return r.status || 1;
  if (playwright) spawnSync(py.exe, ["-m", "playwright", "install", "chromium"], { cwd: SKILL_HOME, stdio: "inherit" });
  if (index && !existsSync(join(SKILL_HOME, "index", "ai-dom.json"))) {
    out("> python index/build_index.py   (starts Illustrator; takes a minute)");
    r = spawnSync(py.exe, ["index/build_index.py"], { cwd: SKILL_HOME, stdio: "inherit" });
    if (r.status !== 0) err("Index build failed — is Illustrator installed and able to start? Re-run: illustrator-com setup");
  }
  return doctor(state);
}

// ---------- npm registry / update ----------------------------------------------------------------------------------

async function registry(path = "") {
  const res = await fetch(REGISTRY + path, { signal: AbortSignal.timeout(5000), headers: { accept: "application/json" } });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`npm registry: HTTP ${res.status}`);
  return res.json();
}
function newer(a, b) {                                     // semver a > b (x.y.z, prerelease ignored)
  const pa = a.split("-")[0].split(".").map(Number), pb = b.split("-")[0].split(".").map(Number);
  for (let i = 0; i < 3; i++) if ((pa[i] || 0) !== (pb[i] || 0)) return (pa[i] || 0) > (pb[i] || 0);
  return false;
}

function isGlobalInstall() {
  const r = spawnSync("npm", ["root", "-g"], { encoding: "utf8", shell: true });
  return r.status === 0 && PKG_ROOT.toLowerCase().startsWith(r.stdout.trim().toLowerCase());
}

async function update(state, { checkOnly = false } = {}) {
  const installed = state.version || PKG.version;
  if (state.linked) { out(`Runtime is linked to a checkout (${realpathSync(SKILL_HOME)}): update it with git pull, then run: illustrator-com sync`); return 0; }
  let latest;
  try { latest = await registry("/latest"); } catch (e) { err(`Update check failed: ${e.message}`); return 1; }
  if (!latest) { out(`${NAME} is not on npm yet — nothing to update from.`); return 0; }
  state.lastCheck = Date.now(); state.latest = latest.version; saveState(state);
  if (!newer(latest.version, installed)) { out(`Up to date (${installed}).`); return 0; }
  out(`Update available: ${installed} -> ${latest.version}`);
  if (checkOnly) return 0;
  if (isGlobalInstall()) {
    out(`> npm install -g ${NAME}@${latest.version}`);
    const r = spawnSync("npm", ["install", "-g", `${NAME}@${latest.version}`], { stdio: "inherit", shell: true });
    if (r.status !== 0) return r.status || 1;
    return spawnSync("illustrator-com", ["sync"], { stdio: "inherit", shell: true }).status ?? 1;
  }
  out(`> npx -y ${NAME}@${latest.version} sync`);
  return spawnSync("npx", ["-y", `${NAME}@${latest.version}`, "sync"], { stdio: "inherit", shell: true }).status ?? 1;
}

async function check(state, { quiet = false } = {}) {
  const cfg = state.config || {};
  const hours = cfg.checkHours ?? 24;
  const fresh = state.lastCheck && Date.now() - state.lastCheck < hours * 3600 * 1000;
  const installed = state.version || PKG.version;
  if (!fresh && !state.linked) {
    try { const l = await registry("/latest"); state.lastCheck = Date.now(); state.latest = l ? l.version : null; saveState(state); }
    catch { if (!quiet) err("Update check failed (offline?)."); return 0; }
  }
  if (state.latest && newer(state.latest, installed)) {
    if (cfg.autoUpdate) return update(state);
    out(`illustrator-com-skill ${state.latest} is available (installed ${installed}). Update: illustrator-com update   `
      + `(or: npx -y ${NAME}@latest sync)`);
  } else if (!quiet) out(`Up to date (${installed}${state.linked ? ", linked checkout" : ""}).`);
  return 0;
}

// ---------- commands -----------------------------------------------------------------------------------------------

async function pickPlatforms() {
  const ps = platforms();
  out("Install for which AI assistant(s)?\n");
  ps.forEach((p, i) => out(`  ${String(i + 1).padStart(2)}. ${p.displayName.padEnd(30)} (${p.platform})`));
  out(`  ${String(ps.length + 1).padStart(2)}. all\n`);
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  const a = (await rl.question("Numbers or keys, comma-separated: ")).trim();
  rl.close();
  const keys = [];
  for (const t of a.split(/[,\s]+/).filter(Boolean)) {
    if (t === "all" || t === String(ps.length + 1)) return ps.map((p) => p.platform);
    const n = Number(t);
    if (n >= 1 && n <= ps.length) keys.push(ps[n - 1].platform);
    else keys.push(platform(t).platform);
  }
  if (!keys.length) throw new Error("No platform selected.");
  return keys;
}

async function init(state, o) {
  const keys = !o.ai ? await pickPlatforms() : o.ai === "all" ? platforms().map((p) => p.platform) : o.ai.split(",").map((k) => platform(k.trim()).platform);
  if (o.link) linkRuntime(state, o.force);
  else {
    const r = syncRuntime(state, { dryRun: o.dryRun });
    out(`Runtime ${o.dryRun ? "(dry run) " : ""}-> ${SKILL_HOME}  (${r.linked ? "linked checkout" : `${r.copied} file(s) copied`}${r.backedUp ? `, ${r.backedUp} edited file(s) backed up to ${r.backupDir}` : ""})`);
  }
  if (!state.python) { const py = findPython(); if (py) state.python = py; }
  let failed = 0;
  for (const k of keys) {
    const cfg = platform(k);
    const file = targetFor(cfg, o);
    if (!file) { out(`  - ${cfg.displayName}: no global location; skipped (install it inside a project without -g)`); continue; }
    const inst = { platform: k, file, scope: o.to ? "custom" : o.global ? "global" : "project" };
    let size;
    try { size = writeAdapter(inst, state, { force: !!o.force, dryRun: o.dryRun }); }
    catch (e) { err(`  ✗ ${cfg.displayName}: ${e.message}`); failed++; continue; }
    out(`  ✓ ${cfg.displayName.padEnd(30)} ${file}  (${size.toLocaleString()} bytes)${cfg.note ? "\n      " + cfg.note : ""}`);
    if (!o.dryRun) {
      state.installs = (state.installs || []).filter((x) => x.file.toLowerCase() !== file.toLowerCase());
      state.installs.push(inst);
    }
  }
  if (o.dryRun) { out("\n(dry run; nothing written)"); return failed ? 1 : 0; }
  saveState(state);
  if (failed) return 1;
  out(existsSync(join(SKILL_HOME, "index", "ai-dom.json")) ? "\nDone." : "\nNext: illustrator-com setup   (Python packages + API index from your Illustrator)");
  return 0;
}

function sync(state) {
  const r = syncRuntime(state);
  out(`Runtime ${PKG.version} -> ${SKILL_HOME}  (${r.linked ? "linked checkout" : `${r.copied} copied, ${r.removed} removed`}${r.backedUp ? `, ${r.backedUp} edited file(s) backed up to ${r.backupDir}` : ""})`);
  const keep = [];
  for (const inst of state.installs || []) {
    if (inst.scope === "project" && !existsSync(dirname(dirname(dirname(inst.file))))) { out(`  - gone: ${inst.file}`); continue; }
    try { writeAdapter(inst, state); keep.push(inst); out(`  ✓ ${inst.platform.padEnd(12)} ${inst.file}`); }
    catch (e) { err(`  ✗ ${inst.file}: ${e.message}`); keep.push(inst); }
  }
  state.installs = keep; state.lastCheck = Date.now(); state.latest = PKG.version;
  saveState(state);
  return 0;
}

function uninstall(state, o) {
  const all = o.ai === "all" || !o.ai;
  const keys = all ? null : o.ai.split(",").map((s) => s.trim());
  const keep = [];
  for (const inst of state.installs || []) {
    if (keys && !keys.includes(inst.platform)) { keep.push(inst); continue; }
    if (existsSync(inst.file)) { unlinkSync(inst.file); try { rmdirSync(dirname(inst.file)); } catch { /* not empty */ } }
    out(`  removed ${inst.file}`);
  }
  state.installs = keep; saveState(state);
  if (o.purge && all) {
    if (isLink(SKILL_HOME)) unlinkSync(SKILL_HOME);
    else rmSync(SKILL_HOME, { recursive: true, force: true });
    out(`  removed runtime ${SKILL_HOME} (including the API index)`);
  } else if (all) out(`Runtime kept at ${SKILL_HOME} (your API index is there). Remove it too with --purge.`);
  return 0;
}

function list() {
  out(`${"platform".padEnd(13)}${"name".padEnd(32)}project path / global path`);
  out("-".repeat(96));
  for (const p of platforms()) {
    const f = p.folderStructure;
    const g = f.globalRoot ? posix(join(f.globalRoot, f.globalSkillPath || f.skillPath)) : "(project only)";
    out(`${p.platform.padEnd(13)}${p.displayName.padEnd(32)}${posix(join(f.root, f.skillPath))}  |  ${g}`);
  }
  out(`\n14 platforms. Install: illustrator-com init --ai <platform>[,<platform>…|all] [-g]`);
  return 0;
}

function info(state) {
  const { fm } = skillSource();
  out(`${NAME} ${PKG.version}\n${PKG.description}\n`);
  out(`Skill name:   ${fm.name}`);
  out(`Runtime home: ${SKILL_HOME}${state.linked ? " (linked)" : ""}  installed ${state.version || "-"}`);
  out(`Auto-update:  ${state.config?.autoUpdate ? "on" : "off"} (check every ${state.config?.checkHours ?? 24} h)`);
  out(`Installs:     ${(state.installs || []).length}`);
  for (const i of state.installs || []) out(`  ${i.platform.padEnd(12)} ${i.scope.padEnd(8)} ${i.file}`);
  out(`\nHomepage: ${PKG.homepage}`);
  return 0;
}

async function versions() {
  let doc;
  try { doc = await registry(); } catch (e) { err(e.message); return 1; }
  if (!doc) { out(`${NAME} is not on npm yet.`); return 0; }
  const vs = Object.keys(doc.versions || {}).sort((a, b) => (newer(a, b) ? -1 : 1));
  for (const v of vs) out(`${v.padEnd(10)} ${(doc.time?.[v] || "").slice(0, 10)}${v === doc["dist-tags"]?.latest ? "  latest" : ""}${v === PKG.version ? "  (this)" : ""}`);
  return 0;
}

function config(state, key, value) {
  state.config = state.config || { autoUpdate: false, checkHours: 24 };
  if (!key) { out(JSON.stringify(state.config, null, 2)); return 0; }
  if (key === "auto-update") {
    if (!["on", "off"].includes(value)) { err("config auto-update on|off"); return 1; }
    state.config.autoUpdate = value === "on";
  } else if (key === "check-hours") {
    const n = Number(value);
    if (!(n > 0)) { err("config check-hours <hours>"); return 1; }
    state.config.checkHours = n;
  } else { err(`Unknown setting "${key}" (auto-update, check-hours)`); return 1; }
  saveState(state);
  out(`${key} = ${value}`);
  return 0;
}

const HELP = `illustrator-com ${PKG.version} — Adobe Illustrator (Windows, COM) skill for AI coding assistants

Usage: illustrator-com <command> [options]

  init [-a, --ai <platform[,…]|all>] [-g, --global] [--to DIR] [--link] [-f] [--dry-run]
                     install the runtime and the SKILL.md for the chosen assistant(s)
  setup [--playwright] [--no-index]
                     pip install -r requirements.txt, build the API index from your Illustrator, run doctor
  doctor [--smoke]   check Windows, Python, packages, Illustrator COM, index (--smoke runs a script in Illustrator)
  list               the 14 supported AI platforms and where each one reads skills
  info | status      version, runtime home, auto-update setting, recorded installs
  versions           versions published on npm
  update [--check]   install the latest npm version into the runtime and every recorded install
  check [--quiet]    update check (cached); updates by itself when auto-update is on
  config [auto-update on|off | check-hours <n>]
  sync               re-copy this package into the runtime and rewrite every recorded SKILL.md
  uninstall [-a <platform[,…]|all>] [--purge]

  --link             point the runtime at this checkout instead of copying (for developing the skill)
  env ILLUSTRATOR_COM_SKILL_HOME   runtime location (default ~/.illustrator-com-skill)
`;

function parse(argv) {
  const o = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "-a" || a === "--ai") o.ai = argv[++i];
    else if (a.startsWith("--ai=")) o.ai = a.slice(5);
    else if (a === "-g" || a === "--global") o.global = true;
    else if (a === "-f" || a === "--force") o.force = true;
    else if (a === "--to") o.to = argv[++i];
    else if (a === "--link") o.link = true;
    else if (a === "--dry-run") o.dryRun = true;
    else if (a === "--smoke") o.smoke = true;
    else if (a === "--quiet" || a === "-q") o.quiet = true;
    else if (a === "--check") o.check = true;
    else if (a === "--purge") o.purge = true;
    else if (a === "--playwright") o.playwright = true;
    else if (a === "--no-index") o.noIndex = true;
    else if (a === "-h" || a === "--help") o.help = true;
    else if (a === "-V" || a === "--version") o.version = true;
    else o._.push(a);
  }
  return o;
}

async function main() {
  const o = parse(process.argv.slice(2));
  if (o.version) { out(PKG.version); return 0; }
  const cmd = o._[0];
  if (!cmd || o.help || cmd === "help") { out(HELP); return 0; }
  const state = loadState();
  switch (cmd) {
    case "init": case "install": return init(state, o);
    case "setup": return setup(state, { playwright: o.playwright, index: !o.noIndex });
    case "doctor": return doctor(state, { smoke: o.smoke });
    case "list": return list();
    case "info": case "status": return info(state);
    case "versions": return versions();
    case "update": return update(state, { checkOnly: o.check });
    case "check": return check(state, { quiet: o.quiet });
    case "config": return config(state, o._[1], o._[2]);
    case "sync": return sync(state);
    case "uninstall": return uninstall(state, o);
    default: err(`Unknown command "${cmd}".\n`); out(HELP); return 1;
  }
}

main().then((c) => process.exit(c ?? 0)).catch((e) => { err(`Error: ${e.message}`); process.exit(1); });
