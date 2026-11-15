"""Query the Illustrator ExtendScript API (reads index/ai-dom.json, built by build_index.py from YOUR Illustrator's
type library plus runtime checks).

Usage:
  python index/ai_api.py find <words...>       search names and Adobe's help text (all words must match), ranked
  python index/ai_api.py class <Class>         properties and methods of a class (type, read-only, arguments, help)
  python index/ai_api.py enum <Enum>           enum members, spelled the ExtendScript way (BlendModes.MULTIPLY)
  python index/ai_api.py member <Class.member> one member in full
  python index/ai_api.py effect [words]        live effects known to work with pageItem.applyEffect(xml) (presets/effects.json)
  python index/ai_api.py menu [words]          menu commands (index/menu-index.json) with coverage status
  python index/ai_api.py stats                 index coverage
Chinese words (zh_TW Illustrator labels or designer wording) are mapped through index/terms_zh.csv and
index/glossary_zh.csv: `menu 建立外框`, `effect 陰影`, `find 陰影`.
Options: --all  also show members not verified at runtime and COM-only members (hidden by default)
Marks:   ✓ exists in ExtendScript on this machine   ? in the type library, not verified   COM  COM-only (ExtendScript: see js_equiv)
"""
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
SKILL = HERE.parent
sys.stdout.reconfigure(encoding="utf-8")
D = json.loads((HERE / "ai-dom.json").read_text(encoding="utf-8"))
ALL = "--all" in sys.argv
args = [x for x in sys.argv[1:] if x != "--all"]


CJK = re.compile("[㐀-鿿]")
_ZH = None


def zh_rows(term):
    """Glossary rows whose Chinese label contains the term (index/terms_zh.csv + index/glossary_zh.csv)."""
    global _ZH
    if _ZH is None:
        _ZH = []
        for f in ("terms_zh.csv", "glossary_zh.csv"):
            p = HERE / f
            if p.exists():
                with open(p, encoding="utf-8", newline="") as fh:
                    _ZH += list(csv.DictReader(fh))
    return [r for r in _ZH if term in r["zh"]]


def matcher(t, field="cmd"):
    """A predicate for one query word: English words are a regex on the text; Chinese words match the commands
    (field="cmd") or the English words (field="words") their glossary rows point to."""
    if not CJK.search(t):
        rx = re.compile(re.escape(t), re.I)
        return lambda text, cmd="": bool(rx.search(text))
    rows = zh_rows(t)
    cmds = {r["cmd"] for r in rows if r["cmd"]}
    words = {w for r in rows for w in (r.get("dom_words") or "").split()}
    words |= {r["en_path"].split(" > ")[-1] for r in rows if r["en_path"] and not r.get("dom_words")}
    rxs = [re.compile(re.escape(w), re.I) for w in words]
    if field == "cmd":
        return lambda text, cmd="": cmd in cmds or t in text
    return lambda text, cmd="": any(r.search(text) for r in rxs)


def mark(x):
    return "COM" if x.get("com_only") else ("✓" if x.get("verified") else "?")


def show(x):
    return ALL or (x.get("verified") and not x.get("com_only"))


def sig(m):
    a = ", ".join(("[" if p["optional"] else "") + f"{p['name']}:{p['type']}" + ("]" if p["optional"] else "") for p in m["args"])
    return f"{m['js']}({a}) → {m['returns']}"


def find(coll, n):
    n = n.lower()
    for k, v in D[coll].items():
        if k.lower() == n or (v.get("js") or "").lower() == n:
            return k


def cmd_class(n):
    k = find("classes", n) or sys.exit(f"no class {n}; try: find {n}")
    c = D["classes"][k]
    print(f"{k} — {c['help']}   (instance: {c['runtime'] or 'could not be created in the sandbox'})")
    print("properties:")
    for p, x in sorted(c["props"].items(), key=lambda i: i[1]["js"].lower()):
        if show(x):
            print(f"  {mark(x)} {x['js']}: {x['type']}{' (read-only)' if x['readonly'] else ''}   {x['help']}" + (f"  → {x['js_equiv']}" if x.get("com_only") else ""))
    print("methods:")
    for m, x in sorted(c["methods"].items(), key=lambda i: i[1]["js"].lower()):
        if show(x):
            print(f"  {mark(x)} {sig(x)}   {x['help']}" + (f"  → {x['js_equiv']}" if x.get("com_only") else ""))
    if c.get("js_only"):
        print("ExtendScript-only (not in the type library):", ", ".join(c["js_only"]))


def cmd_enum(n):
    k = find("enums", n) or sys.exit(f"no enum {n}; try: find {n}")
    e = D["enums"][k]
    print(f"{e['js'] or k} — {e['help']}")
    for m, x in e["members"].items():
        if show(x):
            print(f"  {mark(x)} {x['js'] or m} = {x['value']}   {x['help']}")


def cmd_member(q):
    cn, _, mn = q.partition(".")
    k = find("classes", cn)
    if k:
        for group in ("props", "methods"):
            for n, x in D["classes"][k][group].items():
                if mn.lower() in (n.lower(), x["js"].lower()):
                    print(json.dumps({"class": k, "member": n, **x}, ensure_ascii=False, indent=1))
                    return
    k = find("enums", cn)
    if k:
        for n, x in D["enums"][k]["members"].items():
            if mn.lower() in (n.lower(), (x["js"] or "").split(".")[-1].lower()):
                print(json.dumps({"enum": k, "member": n, **x}, ensure_ascii=False, indent=1))
                return
    sys.exit(f"not found: {q}")


def cmd_find(terms):
    pats = [matcher(t, "words") for t in terms]
    hits = []

    def score(name, text):
        if not all(p(name + " " + text) for p in pats):
            return 0
        return sum(3 if p(name) else 1 for p in pats)

    for k, c in D["classes"].items():
        s = score(k, c["help"])
        if s:
            hits.append((s + 2, f"class {k}   {c['help']}"))
        for group in ("props", "methods"):
            for n, x in c[group].items():
                if not show(x):
                    continue
                s = score(x["js"], x["help"] + " " + k)
                if s:
                    hits.append((s, f"{mark(x)} {k}.{sig(x) if group == 'methods' else x['js'] + ': ' + str(x['type'])}   {x['help']}"))
    for k, e in D["enums"].items():
        s = score(e["js"] or k, e["help"])
        if s:
            hits.append((s + 1, f"enum {e['js'] or k}   {e['help']} ({len(e['members'])} members)"))
        for n, x in e["members"].items():
            if show(x):
                s = score(x["js"] or n, x["help"] + " " + k)
                if s:
                    hits.append((s, f"{mark(x)} {x['js']}   {x['help']}"))
    hits.sort(key=lambda h: -h[0])
    for _, line in hits[:60]:
        print(line)
    if len(hits) > 60:
        print(f"... {len(hits)} hits, narrow the words")
    if not hits:
        print("no hits (try --all, or English words)")
        for t in terms:
            for r in zh_rows(t) if CJK.search(t) else []:
                if r["en_path"]:
                    kind = "effect" if r["en_path"].startswith("Effect >") else "menu"
                    print(f"  {r['zh']} = {r['en_path']}  ->  ai_api.py {kind} {t}")


def cmd_stats():
    C = list(D["classes"].values())
    print(f"source: {D['source']} | Illustrator {D['version']}")
    print(f"classes: {len(C)} ({sum(1 for c in C if c['runtime'])} instantiated at runtime)")
    for g in ("props", "methods"):
        xs = [x for c in C for x in c[g].values()]
        print(f"{g}: {sum(x['verified'] for x in xs)} verified in ExtendScript, {sum(1 for x in xs if x.get('com_only'))} COM-only, "
              f"{sum(1 for x in xs if not x['verified'] and not x.get('com_only'))} unverified, of {len(xs)}")
    ms = [m for e in D["enums"].values() for m in e["members"].values()]
    print(f"enum members: {sum(m['verified'] for m in ms)}/{len(ms)} verified | enums {len(D['enums'])}")


def cmd_effect(terms):
    p = SKILL / "presets" / "effects.json"
    if not p.exists():
        sys.exit("presets/effects.json missing: run python tests/effects_sweep.py")
    E = json.loads(p.read_text(encoding="utf-8"))
    pats = [matcher(t) for t in terms]
    for e in E["effects"]:
        text = f"{e['name']} {e.get('menu', '')} {' '.join(e.get('params', {}))}"
        if all(p(text, e.get("cmd", "")) for p in pats):
            print(f"{'✓' if e.get('ok') else '✗'} {e.get('menu', ''):<40} {e['name']}")
            print(f"    {e['xml']}")


def cmd_menu(terms):
    p = HERE / "menu-index.json"
    if not p.exists():
        sys.exit("index/menu-index.json missing: run python index/build_menu_index.py")
    M = json.loads(p.read_text(encoding="utf-8"))
    cov = {}
    cp = SKILL / "tests" / "coverage.json"
    if cp.exists():
        cov = {r["cmd"]: r for r in json.loads(cp.read_text(encoding="utf-8"))["rows"]}
    pats = [matcher(t) for t in terms]
    for it in M["items"]:
        text = f"{it['cmd']} {it['path']} {it.get('zh', '')}"
        if all(p(text, it["cmd"]) for p in pats):
            c = cov.get(it["cmd"], {})
            print(f"{c.get('status', '·'):<4} {it['path']:<60} app.executeMenuCommand('{it['cmd']}')" + (f"   {c['how']}" if c.get("how") else ""))


if not args:
    sys.exit(__doc__)
cmd, rest = args[0], args[1:]
{"find": lambda: cmd_find(rest), "class": lambda: cmd_class(rest[0]), "enum": lambda: cmd_enum(rest[0]),
 "member": lambda: cmd_member(rest[0]), "stats": cmd_stats, "effect": lambda: cmd_effect(rest),
 "menu": lambda: cmd_menu(rest)}.get(cmd, lambda: sys.exit(__doc__))()
