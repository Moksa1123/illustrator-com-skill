"""Design-size presets: look up recommended sizes for social / e-commerce platforms, or open that size as a new
Illustrator document (artboard in px, safe-zone guides on a locked 'Guides' layer, optional background).
Data: presets/sizes.json (every entry has its source and check date; confidence = official | widely-cited)
Usage:
  python tools/sizes.py list [platform or keyword]      # list ig, list 電商, list story
  python tools/sizes.py show <id>                       # size, ratio, safe zone, file limit, source
  python tools/sizes.py new <id> [--name N] [--bg R,G,B] [--margin px] [--artboards n]
  python tools/sizes.py md                              # Markdown table (docs/sizes.md)
"""
import argparse
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
DATA = json.loads((SKILL / "presets" / "sizes.json").read_text(encoding="utf-8"))
ITEMS = DATA["sizes"]


def match(it, q):
    """every word must hit: whole words of tags / id parts / platform name; non-ASCII words match the Chinese name as substrings"""
    words = set(str(it.get("tags", "")).lower().split()) | set(it["id"].lower().split("_")) | set(it["platform"].lower().replace("(", " ").replace(")", " ").split())
    zh = (it.get("name_zh", "") + " " + it.get("group", "")).lower()
    return all(w in words or (not w.isascii() and w in zh) for w in q.lower().split())


def row(it):
    safe = "" if not it.get("safe") else "  safe L{0} T{1} R{2} B{3}".format(*it["safe"])
    return f"{it['id']:<34} {it['w']:>5}×{it['h']:<5} {it.get('ratio', ''):<7} {it['platform']:<16} {it.get('name_zh', '')}{safe}"


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("q", nargs="*")
    p = sub.add_parser("show"); p.add_argument("id")
    p = sub.add_parser("new"); p.add_argument("id"); p.add_argument("--name"); p.add_argument("--bg"); p.add_argument("--margin", type=int); p.add_argument("--artboards", type=int)
    sub.add_parser("md")
    a = ap.parse_args()
    if a.cmd == "list":
        hits = [it for it in ITEMS if not a.q or match(it, " ".join(a.q))]
        for it in hits:
            print(row(it))
        print(f"({len(hits)} presets; data checked {DATA['checked']})")
    elif a.cmd == "show":
        it = next((x for x in ITEMS if x["id"] == a.id), None) or sys.exit(f"not found: {a.id}; try list")
        print(json.dumps(it, ensure_ascii=False, indent=1))
    elif a.cmd == "new":
        it = next((x for x in ITEMS if x["id"] == a.id), None) or sys.exit(f"not found: {a.id}; try list")
        sys.path.insert(0, str(SKILL / "lib"))
        from ai_run import run_js
        from ailib_loader import library
        opt = {"safe": it.get("safe"), "margin": a.margin, "units": "px", "artboards": a.artboards or 1}
        if a.bg:
            opt["bg"] = [int(v) for v in a.bg.split(",")]
        js = library() + f"var D = AI.newDoc({it['w']}, {it['h']}, {json.dumps(a.name or it['id'])}, {json.dumps(opt)}); var ab = AI.ab(0); var g = 0; try {{ g = D.layers.getByName('Guides').pathItems.length; }} catch (e) {{}} J({{w: ab.w, h: ab.h, artboards: D.artboards.length, guides: g}});"
        print(run_js(js))
    elif a.cmd == "md":
        groups = {}
        for it in ITEMS:
            groups.setdefault(it["group"], []).append(it)
        for g, its in groups.items():
            print(f"\n### {g}\n\n| id | Size | Ratio | Safe zone (L,T,R,B) | Note |\n|---|---|---|---|---|")
            for it in its:
                safe = ", ".join(map(str, it["safe"])) if it.get("safe") else "—"
                src = it.get("source", "")
                src = f"[link]({src})" if src.startswith("http") else src
                print(f"| `{it['id']}` | {it['w']}×{it['h']} | {it.get('ratio', '')} | {safe} | {it.get('name_en', '')} | {it.get('confidence', '')} | {src} |")


if __name__ == "__main__":
    main()
