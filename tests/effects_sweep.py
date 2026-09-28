"""Effects sweep: every Effect-menu command, turned into a dialog-free pageItem.applyEffect(xml) call and verified.

For each Live effect command in index/menu-index.json:
  1. discover  run app.executeMenuCommand(cmd) on a sandbox rectangle, accept the dialog with its defaults,
               save an uncompressed .ai and read back the effect Illustrator actually stored (internal name + typed params)
  2. generate  build the LiveEffect XML from those params
  3. verify    in a fresh document apply the XML with one numeric parameter CHANGED, save, read back:
               the effect must be there and every parameter we passed must come back with our value
Output: presets/effects.json (read by index/ai_api.py effect, lib/ailib.jsx AI.fx), tests/effects-sweep.json
Usage:  python tests/effects_sweep.py [--only words]
"""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL / "lib"))
sys.path.insert(0, str(SKILL / "tools"))
sys.stdout.reconfigure(encoding="utf-8")
import ai_dialogs  # noqa: E402
import ai_dump  # noqa: E402
import ai_run  # noqa: E402
from ai_run import run_js  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--only")
ap.add_argument("--failed", action="store_true")
a = ap.parse_args()

PRE = (SKILL / "lib" / "json.jsx").read_text(encoding="utf-8") + (HERE / "sandbox.jsx").read_text(encoding="utf-8")
TMP = Path(run_js(PRE + "Folder(TMP).fsName"))
MENU = json.loads((SKILL / "index" / "menu-index.json").read_text(encoding="utf-8"))["items"]
SKIPCMD = {"Live Rasterize Effect Setting": "document setting, not an effect (tested in menu sweep)",
           "SVG Filter Import": "opens a file dialog to import an SVG filter file"}
cases = [it for it in MENU if it["top"] == "Effect" and it["cmd"].startswith("Live ") and it["cmd"] not in SKIPCMD]
if a.only:
    cases = [c for c in cases if all(w.lower() in (c["cmd"] + " " + c["path"]).lower() for w in a.only.split())]
if a.failed and (HERE / "effects-sweep.json").exists():
    _done = {r["cmd"] for r in json.loads((HERE / "effects-sweep.json").read_text(encoding="utf-8")) if r["ok"]}
    cases = [c for c in cases if c["cmd"] not in _done]

SETUP = "CLOSEALL(); NEWDOC(); var r = RECT(600, 200, 300, 200); SEL([r]); SAVEAI(TMP + '/_fx_a.ai'); 'ok'"
# Pathfinder effects act on a group of overlapping shapes
SETUP_PF = ("CLOSEALL(); NEWDOC(); var g = app.activeDocument.groupItems.add(); var r = RECT(600, 200, 300, 200); var e = ELLIPSE(550, 350, 250, 250); "
            "r.move(g, ElementPlacement.PLACEATEND); e.move(g, ElementPlacement.PLACEATBEGINNING); SEL([g]); SAVEAI(TMP + '/_fx_a.ai'); 'ok'")


def setup_for(cmd):
    return SETUP_PF if "Pathfinder" in cmd else SETUP


def key(e):
    return json.dumps({"n": e["name"], "p": e["params"]}, sort_keys=True)


def new_effects(before, after):
    pool = [key(e) for e in before]
    out = []
    for e in after:
        k = key(e)
        if k in pool:
            pool.remove(k)
        elif e["name"] != "Conduit Filter":
            out.append(e)
    return out


PSKIP = ("dataSize", "go", "PrevDres", "PrevDocScale")


def tweak(params, types):
    """Change one numeric parameter so the readback proves our value (not the default) was used."""
    p = dict(params)
    for k, v in params.items():
        t = types.get(k)
        if " " in k or k.startswith("Prev") or k in ("DisplayString",) + PSKIP:
            continue
        if t == "Real" and isinstance(v, float):
            p[k] = round(v * 1.5 + 1, 3) if abs(v) < 1e4 else v
            return p, k
    for k, v in params.items():
        if types.get(k) == "Int" and isinstance(v, int) and k not in ("blnd", "csrc", "DeformStyle", "ProcessFillStyle") + PSKIP and " " not in k and not k.startswith("Prev"):
            p[k] = v + 1
            return p, k
    return p, None


def cleanup():
    for _ in range(3):
        if not ai_dialogs.dialogs():
            break
        ai_dialogs.answer_all("esc")
        time.sleep(0.5)


def xml_for(e, params):
    ps = "ps" in e["params"]
    pp = {k: v for k, v in params.items() if not (ps and k in PSKIP)}
    return ai_dump.to_xml(e["name"], pp, e["types"])


def gallery_case(it):
    """Effect > Effect Gallery opens the gallery with no filter chosen: expand the first folder, click its first
    thumbnail (measured from the dialog's top-right corner), OK, and read the chosen filter back from the file."""
    row = {"cmd": it["cmd"], "menu": it["path"], "ok": False}
    run_js(PRE + SETUP)
    run_js(PRE + f"app.executeMenuCommand({json.dumps(it['cmd'])}); SAVEAI(TMP + '/_fx_b.ai'); 'ok'",
           dialog=["wait:3", "clickrel:-673:61", "wait:1.5", "clickrel:-641:102", "wait:3", "ok"], timeout=240)
    found = [x for x in new_effects(ai_dump.effects(TMP / "_fx_a.ai"), ai_dump.effects(TMP / "_fx_b.ai")) if x["name"].startswith("PSAdapter_plugin_")]
    if found:
        row.update({"ok": True, "name": found[0]["name"], "params": found[0]["params"], "types": found[0]["types"],
                    "detail": f"UI: gallery filter chosen by click -> {found[0]['name']} {found[0]['params'].get('ps')} read back; each gallery filter also has its own command"})
    else:
        row["detail"] = "gallery closed without a filter"
    return row


def run_case(it):
    cmd = it["cmd"]
    if cmd == "Live PSAdapter_plugin_GEfc":
        return gallery_case(it)
    row = {"cmd": cmd, "menu": it["path"], "ok": False}
    try:
        cleanup()
        run_js(PRE + setup_for(cmd))
        run_js(PRE + f"app.executeMenuCommand({json.dumps(cmd)}); SAVEAI(TMP + '/_fx_b.ai'); 'ok'", dialog="enter", timeout=120)
        row["dialogs"] = ai_run.last_dialogs
        found = new_effects(ai_dump.effects(TMP / "_fx_a.ai"), ai_dump.effects(TMP / "_fx_b.ai"))
        if not found:
            row["detail"] = "the menu command added no live effect"
            return row
        e = found[0]
        row.update({"name": e["name"], "params": e["params"], "types": e["types"], "also": [x["name"] for x in found[1:]]})
        row["xml"] = xml_for(e, e["params"])
        ps = "ps" in e["params"]
        p2, changed = (dict(e["params"]), None) if ps else tweak(e["params"], e["types"])
        row["xml_test"] = xml_for(e, p2)
        row["changed"] = changed
        run_js(PRE + ("CLOSEALL(); NEWDOC(); var r = RECT(600, 200, 300, 200); " + ("var g = app.activeDocument.groupItems.add(); var e = ELLIPSE(550, 350, 250, 250); r.move(g, ElementPlacement.PLACEATEND); e.move(g, ElementPlacement.PLACEATBEGINNING); r = g; " if "Pathfinder" in cmd else "") + "SAVEAI(TMP + '/_fx_c.ai'); ") +
               f"r.applyEffect({json.dumps(row['xml_test'])}); SAVEAI(TMP + '/_fx_d.ai'); 'ok'", dialog="esc", timeout=120)
        got = [x for x in new_effects(ai_dump.effects(TMP / "_fx_c.ai"), ai_dump.effects(TMP / "_fx_d.ai")) if x["name"] == e["name"]]
        if not got:
            row["detail"] = f"applyEffect did not add {e['name']}"
            return row
        g = got[0]["params"]
        if ps:
            # parameters live in a binary Photoshop descriptor: set the first dialog field, decode, compare
            nums = [(k, v) for k, v in e["params"]["ps"].items() if isinstance(v, int) and not isinstance(v, bool) and 0 <= v < 1000]
            if not nums:
                row["ok"] = True
                row["detail"] = f"{e['name']}: applyEffect adds it with its defaults ({e['params']['ps']}); no numeric dialog field to set"
                return row
            want = nums[0][1] + 1 if nums[0][1] < 50 else nums[0][1] - 1
            run_js(PRE + setup_for(cmd))
            run_js(PRE + f"app.executeMenuCommand({json.dumps(cmd)}); SAVEAI(TMP + '/_fx_e.ai'); 'ok'", dialog=["wait:1", f"editval:{nums[0][1]}:{want}", "wait:0.5", "ok"], timeout=120)
            got2 = [x for x in new_effects(ai_dump.effects(TMP / "_fx_a.ai"), ai_dump.effects(TMP / "_fx_e.ai")) if x["name"] == e["name"]]
            vals = got2[0]["params"].get("ps", {}) if got2 else {}
            hit = [k for k, v in vals.items() if v == want]
            for fld in range(3):                         # custom dialogs: click into field 0, 1, 2 and type
                if hit:
                    break
                run_js(PRE + setup_for(cmd))
                run_js(PRE + f"app.executeMenuCommand({json.dumps(cmd)}); SAVEAI(TMP + '/_fx_e.ai'); 'ok'", dialog=["wait:1", f"clickedit:{fld}", "end", "back", "back", "back", "back", f"type:{want}", "tab", "wait:0.8", "ok"], timeout=120)
                got2 = [x for x in new_effects(ai_dump.effects(TMP / "_fx_a.ai"), ai_dump.effects(TMP / "_fx_e.ai")) if x["name"] == e["name"]]
                vals = got2[0]["params"].get("ps", {}) if got2 else {}
                hit = [k for k, v in vals.items() if v == want]
            row["ps_dialog"] = {"typed": want, "read": vals}
            row["ok"] = bool(hit)
            row["detail"] = (f"{e['name']}: XML applies it with defaults; dialog field 0 typed {want} -> descriptor {hit[0]}={want} read back" if hit
                             else f"{e['name']}: XML ok, but typed {want} not found in descriptor {vals}")
            return row
        sent = {k: v for k, v in p2.items() if e["types"].get(k) in ("Real", "Int", "Bool") and " " not in k and k != "DisplayString"}
        bad = {k: (v, g.get(k)) for k, v in sent.items() if (abs(float(g.get(k, 1e9)) - float(v)) > 1e-3 if isinstance(v, (int, float)) and not isinstance(v, bool) else g.get(k) != v)}
        row["ok"] = not bad
        row["detail"] = (f"{e['name']}: {len(sent)} params read back" + (f", {changed} changed to {p2[changed]}" if changed else "")) if not bad else f"mismatch {bad}"
    except Exception as ex:  # noqa: BLE001
        row["detail"] = f"error: {str(ex)[:200]}"
        row["fault"] = ai_run.is_fault(ex)
    return row


OUTF = HERE / "effects-sweep.json"
merged = {r["cmd"]: r for r in json.loads(OUTF.read_text(encoding="utf-8"))} if OUTF.exists() else {}


def save():
    OUTF.write_text(json.dumps(list(merged.values()), ensure_ascii=False, indent=1), encoding="utf-8")
    eff = [{"cmd": r["cmd"], "menu": r["menu"], "name": r.get("name"), "ok": r["ok"], "xml": r.get("xml"), "params": r.get("params"),
            "types": r.get("types")} for r in merged.values() if r.get("name")]
    (SKILL / "presets").mkdir(exist_ok=True)
    (SKILL / "presets" / "effects.json").write_text(json.dumps({"illustrator": "28.0.0", "effects": eff}, ensure_ascii=False, indent=1), encoding="utf-8")


for i, it in enumerate(cases):
    t0 = time.time()
    row = run_case(it)
    if row.get("fault") or not ai_run.healthy():
        print("   Illustrator script engine faulted: restarting and retrying once", flush=True)
        ai_run.restart()
        row = run_case(it)
        row["retried"] = True
        if row.get("fault") or not ai_run.healthy():
            ai_run.restart()
    row["ms"] = int((time.time() - t0) * 1000)
    merged[row["cmd"]] = row
    save()
    print(f"{'✅' if row['ok'] else '❌'} {i + 1}/{len(cases)} {it['path']:<55} {row.get('detail', '')}", flush=True)
cleanup()
try:
    run_js(PRE + "CLOSEALL(); 'ok'")
except Exception:  # noqa: BLE001
    pass
print(f"\n{sum(r['ok'] for r in merged.values())}/{len(merged)} effects verified -> presets/effects.json")
