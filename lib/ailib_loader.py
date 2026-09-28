"""Assemble the ExtendScript prelude every script needs: json.jsx + ailib.jsx + AI.FXDB (verified effect defaults
from presets/effects.json, so AI.fx(item, 'Adobe Drop Shadow', {blur: 3}) fills in every other parameter).

from ailib_loader import library; run_js(library() + "AI.rect(0, 0, 100, 100, {fill: '#ff0000'}); 'ok'")
"""
import json
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent


def fxdb():
    p = SKILL / "presets" / "effects.json"
    if not p.exists():
        return {}
    db = {}
    for e in json.loads(p.read_text(encoding="utf-8"))["effects"]:
        if e.get("ok") and e.get("name") and e["name"] not in db:
            db[e["name"]] = {"p": {k: v for k, v in (e.get("params") or {}).items() if (e.get("types") or {}).get(k) in ("Real", "Int", "Bool")},
                             "t": e.get("types") or {}}
    return db


def library():
    src = (SKILL / "lib" / "json.jsx").read_text(encoding="utf-8") + "\n" + (SKILL / "lib" / "ailib.jsx").read_text(encoding="utf-8")
    return src + "\nAI.FXDB = " + json.dumps(fxdb(), ensure_ascii=False) + ";\n"
