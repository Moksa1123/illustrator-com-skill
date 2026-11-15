"""Check every count, version and date written in SKILL.md (and package.json's description) against the data.

SOP 6-1: numbers in SKILL.md are not hand-maintained facts; this script fails when one drifts from the data.
Each check is (label, regex on the text, function returning the actual value(s)). A regex that no longer matches is
a failure too, so a reworded sentence cannot silently escape the check.

Usage: python tools/check_numbers.py      exit 1 on any mismatch
Stdlib only. index/ai-dom.json is built locally (not shipped): its checks are SKIPPED when it is missing.
"""
import csv
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent


def load(rel):
    return json.loads((SKILL / rel).read_text(encoding="utf-8"))


def rows(rel):
    with open(SKILL / rel, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def dom():
    p = SKILL / "index" / "ai-dom.json"
    if not p.exists():
        return None
    D = json.loads(p.read_text(encoding="utf-8"))
    xs = [x for c in D["classes"].values() for g in ("props", "methods") for x in c[g].values()]
    com = sum(1 for x in xs if x.get("com_only"))
    ver = sum(1 for x in xs if x["verified"] and not x.get("com_only"))
    unv = sum(1 for x in xs if not x["verified"] and not x.get("com_only"))
    return {"classes": len(D["classes"]), "members": len(xs), "verified": ver, "com": com, "unverified": unv,
            "version": D["version"]}


def coverage():
    from collections import Counter
    c = Counter(r["status"] for r in load("tests/coverage.json")["rows"])
    return c["✅"], c["n/a"], c["blocked"]


def report():
    t = (SKILL / "tests" / "REPORT.md").read_text(encoding="utf-8")
    m = re.search(r"Illustrator (\S+) \| (\d{4}-\d\d-\d\d)T\S+ \| \*\*(\d+)/(\d+) pass", t)
    return m.group(1), m.group(2), int(m.group(3)), int(m.group(4))


def sizes():
    S = load("presets/sizes.json")
    conf = [s.get("confidence") for s in S["sizes"]]
    return len(S["sizes"]), conf.count("official"), conf.count("widely-cited"), S["checked"]


def effects():
    E = load("presets/effects.json")["effects"]
    return len(E), sum(1 for e in E if e.get("ok"))


def checks():
    menu = len(load("index/menu-index.json")["items"])
    ok, na, blocked = coverage()
    n_eff, n_eff_ok = effects()
    n_sz, n_off, n_wide, sz_date = sizes()
    rv, rdate, rpass, rtotal = report()
    d = dom()
    S = "SKILL.md"
    out = [
        (S, "description: classes", r"\((\d+) classes;", lambda: d and d["classes"]),
        (S, "description: menu commands", r"\((\d+) commands captured", lambda: menu),
        (S, "description: live effects", r"any of (\d+) live effects", lambda: n_eff),
        (S, "description: size presets", r"includes (\d+) design-size presets", lambda: n_sz),
        (S, "sources: DOM row", r"\| (\d+) classes, (\d+) members: (\d+) verified in ExtendScript, (\d+) COM-only, (\d+) unverified \| .*?Illustrator (\S+) \|",
         lambda: d and (d["classes"], d["members"], d["verified"], d["com"], d["unverified"], d["version"])),
        (S, "sources: menu row", r"\| (\d+) menu commands: (\d+) run and read back, (\d+) n/a \(UI/settings\), (\d+) blocked \|",
         lambda: (menu, ok, na, blocked)),
        (S, "sources: effects row", r"\| (\d+) live effects, all applied and read back \|",
         lambda: n_eff if n_eff == n_eff_ok else ("not all ok", n_eff_ok)),
        (S, "sources: terms_zh row", r"\| (\d+) zh_TW-English menu label pairs \|", lambda: len(rows("index/terms_zh.csv"))),
        (S, "sources: glossary row", r"\| (\d+) hand-made design terms \|", lambda: len(rows("index/glossary_zh.csv"))),
        (S, "sources: sizes row", r"\| (\d+) design-size presets \| .*? \| (\d{4}-\d\d-\d\d) \| (\d+) official, (\d+) widely-cited \|",
         lambda: (n_sz, sz_date, n_off, n_wide)),
        (S, "sources: tests row", r"\| (\d+)/(\d+) library tests \| `tests/run_tests.py` in Illustrator (\S+) \| (\d{4}-\d\d-\d\d) \|",
         lambda: (rpass, rtotal, rv, rdate)),
        (S, "verify: last library run", r"last run (\d+)/(\d+), (\d{4}-\d\d-\d\d)", lambda: (rpass, rtotal, rdate)),
        ("package.json", "package: scriptable menu commands", r"(\d+)/(\d+) scriptable menu commands", lambda: (ok, ok)),
        ("package.json", "package: live effects", r"and (\d+) live effects verified", lambda: n_eff),
        ("package.json", "package: size presets", r"(\d+) design-size presets", lambda: n_sz),
    ]
    return out


def conv(found, want):
    """Cast the regex groups to the types of the expected value."""
    if not isinstance(want, tuple):
        want = (want,)
    return tuple(type(w)(f) if isinstance(w, int) else f for f, w in zip(found, want)), want


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    texts = {"SKILL.md": (SKILL / "SKILL.md").read_text(encoding="utf-8"),
             "package.json": load("package.json")["description"]}
    bad = 0
    for src, label, rx, fn in checks():
        m = re.search(rx, texts[src], re.S if "sources" in label else 0)
        want = fn()
        if want is None:
            print(f"SKIP  {label}: index/ai-dom.json not built here")
            continue
        if not m:
            print(f"FAIL  {label}: sentence not found in {src} (pattern {rx})")
            bad += 1
            continue
        got, want = conv(m.groups(), want)
        if got != want:
            print(f"FAIL  {label}: {src} says {got}, data says {want}")
            bad += 1
        else:
            print(f"OK    {label}: {', '.join(map(str, got))}")
    print(f"{'FAIL' if bad else 'PASS'}: {bad} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
