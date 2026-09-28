"""Find the executeMenuCommand string for commands whose shortcut-set name is not accepted.

app.executeMenuCommand(name) throws PARM for an unknown name (and runs the command otherwise), so candidate spellings
can be probed. Candidates: case variants, camelCase split into words, known prefixes/suffixes, and strings found near
the name in Illustrator's own binaries. Runs in a sandbox document with the dialog watchdog cancelling everything.
Output: index/raw/command_aliases.json  {shortcut-set name: executeMenuCommand name}
Usage: python tools/probe_commands.py name [name ...]   (no names: every command the menu sweep saw fail with PARM)
"""
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "lib"))
sys.stdout.reconfigure(encoding="utf-8")
from ai_run import run_js  # noqa: E402


def variants(n):
    base = n.lstrip("~")
    words = re.sub(r"([a-z])([A-Z0-9])", r"\1 \2", base)
    out = [base, n, base.lower(), base[0].upper() + base[1:], words, words.lower(), words.title(), words.capitalize(),
           base.replace("-", " "), base.replace("-", ""), words.replace(" ", "-"), words.title().replace(" ", ""),
           base + " menu item", words + " menu item", "Adobe " + words, "Adobe " + base, base + "2", base + "3",
           words.title() + " menu item"]
    return list(dict.fromkeys(x for x in out if x))


def probe(names):
    js = "var C = " + json.dumps({n: variants(n) + EXTRA.get(n, []) for n in names}) + r""";
if (!app.documents.length) app.documents.add();
var R = {};
for (var k in C) { R[k] = null;
  for (var i = 0; i < C[k].length; i++) { app.activeDocument.selection = null;
    try { app.executeMenuCommand(C[k][i]); R[k] = C[k][i]; break; } catch (e) { if (String(e).indexOf('PARM') < 0) { R[k] = C[k][i]; break; } } } }
var s = []; for (var k in R) s.push(k + '\t' + R[k]); s.join('\n');"""
    return dict(line.split("\t") for line in run_js(js, dialog="esc", timeout=600).split("\n") if "\t" in line)


EXTRA = {}
if __name__ == "__main__":
    names = sys.argv[1:]
    if not names:
        ms = json.loads((SKILL / "tests" / "menu-sweep.json").read_text(encoding="utf-8"))
        names = [r["cmd"] for r in ms if "PARM" in (r.get("detail") or "") and "MENU(c)" in (r.get("detail") or "")]
    res = probe(names)
    p = SKILL / "index" / "raw" / "command_aliases.json"
    old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    for k, v in res.items():
        print(("✅ " if v != "null" else "·  ") + k, "->", v)
        if v != "null":
            old[k] = v
    p.write_text(json.dumps(old, ensure_ascii=False, indent=1), encoding="utf-8")
