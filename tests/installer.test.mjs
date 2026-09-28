// Installer tests in a throw-away USERPROFILE / skill home / project: init for all 14 platforms (project + global),
// SKILL.md content, sync keeping the API index and backing up edited files, foreign-file protection, uninstall.
import { mkdtempSync, readFileSync, writeFileSync, existsSync, readdirSync, mkdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve, dirname } from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const CLI = join(ROOT, "bin", "illustrator-com.mjs");
const T = mkdtempSync(join(tmpdir(), "aicom-"));
const HOME = join(T, "user"), SK = join(T, "skillhome"), PROJ = join(T, "proj");
[HOME, PROJ].forEach((d) => mkdirSync(d, { recursive: true }));
const env = { ...process.env, USERPROFILE: HOME, HOME, ILLUSTRATOR_COM_SKILL_HOME: SK };
let fails = 0, n = 0;
const run = (...a) => spawnSync(process.execPath, [CLI, ...a], { cwd: PROJ, env, encoding: "utf8" });
const ok = (c, msg) => { n++; if (!c) { fails++; console.log("FAIL", msg); } else console.log("ok  ", msg); };
const plats = readdirSync(join(ROOT, "assets", "templates", "platforms")).map((f) => JSON.parse(readFileSync(join(ROOT, "assets", "templates", "platforms", f), "utf8")));

let r = run("list");
ok(r.status === 0 && plats.every((p) => r.stdout.includes(p.platform)) && plats.length === 14, "list shows 14 platforms");

r = run("init", "--ai", "all");
ok(r.status === 0, "init --ai all (project) exits 0 " + r.stderr);
ok(existsSync(join(SK, "lib", "ai_run.py")) && existsSync(join(SK, "bin", "illustrator-com.mjs")), "runtime copied to skill home");
ok(!existsSync(join(SK, "index", "ai-dom.json")) && !existsSync(join(SK, "index", "raw")), "per-machine index is not copied from the checkout");
for (const p of plats) {
  const f = join(PROJ, p.folderStructure.root, p.folderStructure.skillPath, "SKILL.md");
  const s = existsSync(f) ? readFileSync(f, "utf8") : "";
  ok(s.startsWith("---\nname: illustrator-com\ndescription: ") && s.includes(SK) && s.includes("version: ") && s.includes("<!-- installed by illustrator-com-skill"), `project SKILL.md for ${p.platform}`);
}
const sk = readFileSync(join(PROJ, ".claude/skills/illustrator-com/SKILL.md"), "utf8");
ok(sk.includes(`sys.path.insert(0, r"${join(SK, "lib")}")`), "Using-it snippet points at the runtime lib/");
ok(!/\nversion: .*\n[\s\S]*\nversion: /.test(sk.split("\n---\n")[0]), "frontmatter has no duplicate keys");

r = run("init", "--ai", "claude,codex,antigravity,windsurf", "-g");
ok(existsSync(join(HOME, ".claude/skills/illustrator-com/SKILL.md")), "global claude");
ok(existsSync(join(HOME, ".codex/skills/illustrator-com/SKILL.md")), "global codex");
ok(existsSync(join(HOME, ".gemini/antigravity/global_skills/illustrator-com/SKILL.md")), "global antigravity");
ok(r.stdout.includes("no global location"), "windsurf (project-only) skipped with -g");
const st = JSON.parse(readFileSync(join(SK, "_state", "state.json"), "utf8"));
ok(st.installs.length === 17, `state records 17 installs (got ${st.installs.length})`);

// per-machine data survives sync; locally edited runtime file is backed up; foreign SKILL.md protected
writeFileSync(join(SK, "index", "ai-dom.json"), "{}");
writeFileSync(join(SK, "tools", "sizes.py"), "# edited\n");
r = run("sync");
ok(r.status === 0 && readFileSync(join(SK, "index", "ai-dom.json"), "utf8") === "{}", "sync keeps index/ai-dom.json");
ok(readFileSync(join(SK, "tools", "sizes.py"), "utf8") !== "# edited\n" && r.stdout.includes("backed up"), "sync restores + backs up an edited file");
const foreign = join(PROJ, ".kiro/skills/illustrator-com/SKILL.md");
writeFileSync(foreign, "my own file");
r = run("init", "--ai", "kiro");
ok(r.status !== 0 && readFileSync(foreign, "utf8") === "my own file", "init refuses to overwrite a foreign SKILL.md");
r = run("init", "--ai", "kiro", "--force");
ok(r.status === 0 && readFileSync(foreign, "utf8").includes("installed by illustrator-com-skill"), "--force replaces it");

r = run("config", "auto-update", "on");
ok(JSON.parse(readFileSync(join(SK, "_state", "state.json"), "utf8")).config.autoUpdate === true, "config auto-update on");
r = run("init", "--ai", "nope");
ok(r.status !== 0 && /Unknown platform/.test(r.stderr), "unknown platform rejected");
r = run("init", "--ai", "cursor", "--dry-run", "--to", join(T, "dry"));
ok(r.status === 0 && !existsSync(join(T, "dry")), "--dry-run writes nothing");

r = run("uninstall", "--ai", "all");
ok(!existsSync(join(PROJ, ".cursor/skills/illustrator-com/SKILL.md")) && !existsSync(join(HOME, ".claude/skills/illustrator-com")) && existsSync(join(SK, "index", "ai-dom.json")), "uninstall removes adapters, keeps runtime + index");
r = run("uninstall", "--purge");
ok(!existsSync(SK), "uninstall --purge removes the runtime");

rmSync(T, { recursive: true, force: true });
console.log(`\n${n - fails}/${n} passed`);
process.exit(fails ? 1 : 0);
