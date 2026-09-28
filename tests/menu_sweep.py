"""Menu sweep: run every case in tests/menu_cases.py in a fresh Illustrator sandbox document and verify it.

Verdict per case
  readback     the case's check expression is true afterwards
  deep         "deep:a,b" check: the art hash of two saves made during the action differ (tools/ai_dump.py)
  fingerprint  no check: the document fingerprint (DOM parts + art hash of an uncompressed .ai + PNG pixels) changed
Dialogs are handled by the watchdog (lib/ai_run.py): accepted, cancelled, or filled in by the case's plan.
A case that leaves Illustrator's script engine faulted triggers a restart and one retry.
Output: tests/menu-sweep.json (tests/build_coverage.py merges it into CAPABILITIES.md)
Usage:  python tests/menu_sweep.py [--only words] [--kind grp,clip] [--failed] [--start N] [--include-blocked]
"""
import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL / "lib"))
sys.path.insert(0, str(SKILL / "tools"))
sys.path.insert(0, str(HERE))
sys.stdout.reconfigure(encoding="utf-8")
import ai_dialogs  # noqa: E402
import ai_dump  # noqa: E402
import ai_run  # noqa: E402
sys.path.insert(0, str(SKILL / "tools"))
from ai_run import run_js  # noqa: E402
from ailib_loader import library  # noqa: E402
from menu_cases import CASES  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--only")
ap.add_argument("--kind", help="comma list: only cases whose scenario kind contains one of these (e.g. grp,clip)")
ap.add_argument("--failed", action="store_true", help="only re-run cases that are not passing in menu-sweep.json")
ap.add_argument("--start", type=int, default=1, help="resume: skip the first N-1 cases (1-based, in CASES order)")
ap.add_argument("--include-blocked", action="store_true", help="also run cases listed in tests/blocked.json (skipped by default: their evidence is recorded)")
a = ap.parse_args() if __name__ == "__main__" else ap.parse_args([])

OUT = HERE / "menu-sweep.json"
old = {r["cmd"]: r for r in json.loads(OUT.read_text(encoding="utf-8"))} if OUT.exists() else {}
PRE = (library() + (HERE / "sandbox.jsx").read_text(encoding="utf-8") + (SKILL / "lib" / "fingerprint.jsx").read_text(encoding="utf-8")
       + (HERE / "menu_sweep.jsx").read_text(encoding="utf-8") + f"\nvar SKILL = {json.dumps(SKILL.as_posix())};\n")
TMP = Path(run_js(PRE + "Folder(TMP).fsName"))
cases = CASES
if a.kind:
    cases = [c for c in cases if any(k in (c["kind"] or "") for k in a.kind.split(","))]
if a.only:
    cases = [c for c in cases if all(w.lower() in c["cmd"].lower() for w in a.only.split())]
if a.failed:
    cases = [c for c in cases if not old.get(c["cmd"], {}).get("ok")]
if a.start > 1:
    cases = cases[a.start - 1:]
BLOCKED_P = HERE / "blocked.json"
if not a.include_blocked and BLOCKED_P.exists():
    _bl = json.loads(BLOCKED_P.read_text(encoding="utf-8"))
    cases = [c for c in cases if c["cmd"] not in _bl]


def clip_get():
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        try:
            return win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        finally:
            win32clipboard.CloseClipboard()
    except Exception:  # noqa: BLE001
        return None


def clip_set(t):
    if t is None:
        return
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(t, win32clipboard.CF_UNICODETEXT)
        finally:
            win32clipboard.CloseClipboard()
    except Exception:  # noqa: BLE001
        pass


def pixhash(p):
    return hashlib.sha1(Path(p).read_bytes()).hexdigest()[:12] if Path(p).exists() else None


def plan(dlg):
    if isinstance(dlg, list) and dlg and isinstance(dlg[0], list):
        return [plan(x) for x in dlg]
    if isinstance(dlg, list):
        return [s.replace("{TMPW}", str(TMP)) for s in dlg]
    return dlg


# Scenario objects that only a menu command can make (blend, envelope, live paint, repeat): each step is its own call,
# because a command issued in the same call as the objects' creation sees stale targets and silently does nothing.
POST_STEPS = {
    "blend": ["AI.select([N('BLa'), N('BLb')]);", "MENU('Path Blend Make');", "if (NS()) D.selection[0].name = 'BL';"],
    "env": ["AI.select([N('ENsrc')]);", "MENU('Make Warp');", "if (NS()) D.selection[0].name = 'EN';"],
    "lp": ["AI.select([N('LPa'), N('LPb')]);", "MENU('Make Planet X');", "if (NS()) D.selection[0].name = 'LP';"],
    "rep": ["AI.select([N('RPsrc')]);", "MENU('Make Radial Repeat');", "if (D.radialRepeatItems.length) D.radialRepeatItems[0].name = 'RP';"],
}


def ui_menu(path, dlg):
    """Click a menu item through the real menu bar; answer the dialog it opens (plan, or accept) within a few seconds."""
    import menu_ui
    for attempt in range(4):                              # another program can take the foreground: the guard stops, retry
        try:
            menu_ui.menu_click(path)
            break
        except RuntimeError as e:
            if "foreground" not in str(e) or attempt == 3:
                raise
            time.sleep(2)
    seen, t0 = [], time.time()
    while time.time() - t0 < 4:
        ds = ai_dialogs.dialogs()
        if ds:
            h, _, title = ds[0]
            seen.append(title)
            time.sleep(0.6)
            if isinstance(dlg, list):
                ai_dialogs.steps(h, dlg)
                dlg = "enter"
            else:
                ai_dialogs.press(h, dlg if dlg in ("enter", "esc") else "enter")
            t0 = time.time()
        time.sleep(0.3)
    return seen


def post(kind):
    parts = kind.split("+")
    steps = [s for k in parts for s in POST_STEPS.get(k, [])]
    if not steps:
        return
    for st in steps:
        run_js("app.redraw(); REBIND();\n" + st + "\n'ok'", dialog="enter", timeout=120)
        time.sleep(0.2)
    run_js(f"SELECTFOR({json.dumps(kind)}); var __N0 = D.pageItems.length, __P0 = D.pathItems.length, __G0 = D.groupItems.length, __PL0 = D.pluginItems.length, __RP0 = D.radialRepeatItems.length; 'ok'", timeout=60)
    time.sleep(0.2)


def run_case(c):
    act = c["act"] or f"MENU({json.dumps(c['cmd'])});"
    check = c["check"]
    deep_fp = check is None
    js = PRE + "SETUP(" + json.dumps(c["kind"]) + ");\n"
    js += "var __N0 = D.pageItems.length, __P0 = D.pathItems.length, __G0 = D.groupItems.length, __PL0 = D.pluginItems.length, __RP0 = D.radialRepeatItems.length;\n"
    js += "var __F0 = FP();\n"
    if deep_fp:
        js += "SAVEAI(TMP + '/_fp_a.ai'); PNG(TMP + '/_fp_a.png', 50);\n"
    js_setup = js + "'ok'"
    js_act = "app.redraw(); REBIND();\n" + act + "\n'ok'"           # own call: Illustrator refreshes command targets when idle
    js = "REBIND(); var __R = {};\n"
    js += "try { if (app.documents.length) { var __F1 = FP(); __R.diff = FPDIFF(__F0, __F1); } } catch (e) { __R.diff = ['!' + e]; }\n"
    if deep_fp:
        js += "try { SAVEAI(TMP + '/_fp_b.ai'); PNG(TMP + '/_fp_b.png', 50); } catch (e) { __R.saveErr = String(e); }\n"
    if check and not check.startswith(("deep:", "pix:", "menuhas:", "menutoggle:")):
        js += f"try {{ __R.ok = !!({check}); }} catch (e) {{ __R.ok = false; __R.err = String(e); }}\n"
    js += "__R.sel = (function () { try { return NS(); } catch (e) { return -2; } })();\nJ(__R);"
    row = {"cmd": c["cmd"], "how": c["how"], "ok": False}
    clipsave = clip_get() if c.get("clip") else None
    try:
        for f in ("_fp_a.ai", "_fp_b.ai", "_fp_a.png", "_fp_b.png"):
            (TMP / f).unlink(missing_ok=True)
        if check and check.startswith("deep:"):
            for t in check[5:].split(","):
                (TMP / f"_d_{t}.ai").unlink(missing_ok=True)
        # a command right after a scripted selection sees the old targets: split the action after each AI.select(...)
        cut = re.sub(r"(AI\.select\(\[[^\]]*\]\);)", "\\1\x00", act)               # after a scripted selection
        cut = re.sub(r"(^|;\s*)(MENU\(|DEEP\(|SHOT\(|UIMENU\(|UIDRAG\(|UIKEY\(|UIDBL\(|UIEDGE\()", "\\1\x00\\2", cut)         # before every top-level MENU / DEEP / UIMENU
        cut = re.sub(r'((?:UIMENU\(\[[^\]]*\]\)|UIDRAG\(\d+\)|UIKEY\("\w+"\)|UIDBL\(\[[^\]]*\]\)|UIEDGE\(\[[^\]]*\],\s*[\d.]+\));)', "\\1\x00", cut)                      # a UI menu step is a segment of its own
        segs = [x for x in cut.split("\x00") if x.strip()]
        for attempt in range(3):
            try:
                run_js(js_setup, dialog="enter", timeout=180)
                time.sleep(0.8)          # idle after building the scenario (new objects become command targets)
                post(c["kind"])
                run_js("try { app.executeMenuCommand('consolidateAllWindows'); app.executeMenuCommand('fitin'); app.redraw(); } catch (e) {} REBIND(); var __N0 = D.pageItems.length, __P0 = D.pathItems.length, __G0 = D.groupItems.length, __PL0 = D.pluginItems.length, "
                       "__RP0 = D.radialRepeatItems.length, __ST0 = D.stories.length, __LY0 = D.layers.length; var __RZ = R ? R.absoluteZOrderPosition : 0, __RB = R ? R.geometricBounds.join() : ''; 'ok'", timeout=60)     # before-state in its own call
                time.sleep(0.6)          # let Illustrator go idle: consolidate / fitin reset the command targets until the next idle
                dl = []
                queue = plan(c["dlg"])
                plans = isinstance(queue, list) and bool(queue) and isinstance(queue[0], list)
                if check and check.startswith("menutoggle:"):   # labels of that submenu before the action
                    import menu_ui
                    row["_menu_before"] = [lab for lab, on in menu_ui.menu_list(check[11:].split("|"))]
                for k, seg in enumerate(segs):
                    if seg.strip().startswith("UIDRAG("):          # drag the slider of the on-canvas widget the command opened
                        import menu_ui
                        time.sleep(0.8)
                        menu_ui.widget_drag(int(seg.strip()[7:seg.strip().index(")")]))
                        continue
                    if seg.strip().startswith("UIDBL("):           # double-click artwork found on screen by its colour
                        import menu_ui
                        run_js("app.selectTool('Adobe Select Tool'); try { app.executeMenuCommand('fitin'); } catch (e) {} app.redraw(); 'ok'")
                        menu_ui.dblclick_color(tuple(json.loads(seg.strip()[6:seg.strip().rindex(")")])))
                        continue
                    if seg.strip().startswith("UIEDGE("):          # drag the right handle of artwork found by colour (crop widget)
                        import menu_ui
                        a = json.loads("[" + seg.strip()[7:seg.strip().rindex(")")] + "]")
                        menu_ui.edge_drag(tuple(a[0]), a[1])
                        continue
                    if seg.strip().startswith("UIKEY("):           # a key into Illustrator's main window (commit a widget)
                        import ui_drive
                        ui_drive.focus_window(ai_dialogs.main_window())
                        ui_drive.key({"enter": 0x0D, "esc": 0x1B}[json.loads(seg.strip()[6:seg.strip().index(")")])])
                        time.sleep(0.8)
                        continue
                    if seg.strip().startswith("UIMENU("):         # the real menu bar (tools/menu_ui.py), then the dialog plan
                        seen = ui_menu(json.loads(seg.strip()[7:seg.strip().rindex(")")]), (queue[0] if queue else "enter") if plans else queue)
                        dl += seen
                        queue = queue[len(seen):] if plans and seen else queue
                        continue
                    this = (list(queue) if plans else queue) if (k == len(segs) - 1 or "MENU(" in seg) else "enter"
                    run_js("app.redraw(); REBIND();\n" + seg + "\n'ok'", dialog=(this or "enter"), timeout=180)
                    dl += ai_run.last_dialogs
                    if plans and ai_run.last_dialogs:          # a queue of per-dialog plans is consumed across segments
                        queue = queue[len(ai_run.last_dialogs):]
                    time.sleep(1.0 if "MENU(" in seg else 0.6)     # MENU: some commands finish late; others: let the new selection become the command target (idle)
                r = json.loads(run_js(js, dialog="esc", timeout=180))
                row["dialogs"] = dl
                break
            except ai_run.AIError as e:                    # Illustrator crashed and COM relaunched it (globals / document gone): redo the case
                crashed = any(x in str(e) for x in ("there is no document", "REBIND", "SELECTFOR", "SETUP", "-2147023170", "-2147417851"))
                if not crashed or attempt == 2:
                    raise
                row["recovered"] = row.get("recovered", 0) + 1
                if not ai_run.healthy():
                    ai_run.restart()
                time.sleep(2)
        row["diff"] = r.get("diff")
        if check and check.startswith("menutoggle:"):       # a toggle: the submenu's labels change (Lock <-> Unlock ...)
            import menu_ui
            after = [lab for lab, on in menu_ui.menu_list(check[11:].split("|"))]
            before = row.pop("_menu_before", None)
            row["ok"] = bool(before) and before != after
            row["level"] = "menu readback"
            row["detail"] = f"{' > '.join(check[11:].split('|'))}: {sorted(set(before or []) ^ set(after))}"
        elif check and check.startswith("menuhas:"):          # the real menu shows this label afterwards
            import menu_ui
            parts = check[8:].split("|")
            labels = [lab for lab, on in menu_ui.menu_list(parts[:-1])]
            row["ok"] = parts[-1] in labels
            row["level"] = "menu readback"
            row["detail"] = f"{' > '.join(parts[:-1])} now shows '{parts[-1]}'" if row["ok"] else f"labels: {labels}"
        elif check and check.startswith("pix:"):
            x, y = check[4:].split(",")
            pa, pb = pixhash(TMP / f"_p_{x}.png"), pixhash(TMP / f"_p_{y}.png")
            row["ok"] = bool(pa and pb and pa != pb)
            row["level"] = "pixels"
            row["detail"] = f"artboard pixels {pa} -> {pb}"
        elif check and check.startswith("deep:"):
            x, y = check[5:].split(",")
            ha, hb = ai_dump.art_hash(TMP / f"_d_{x}.ai"), ai_dump.art_hash(TMP / f"_d_{y}.ai")
            row["ok"] = ha != hb
            row["level"] = "deep"
            row["detail"] = f"art hash {ha} -> {hb}"
        elif check:
            row["ok"] = bool(r.get("ok"))
            row["level"] = "readback"
            row["detail"] = "check true" if row["ok"] else f"check false {r.get('err', '')}"
        else:
            parts = [d for d in (r.get("diff") or []) if d != "sel"]
            ha = ai_dump.art_hash(TMP / "_fp_a.ai") if (TMP / "_fp_a.ai").exists() else None
            hb = ai_dump.art_hash(TMP / "_fp_b.ai") if (TMP / "_fp_b.ai").exists() else None
            pa, pb = pixhash(TMP / "_fp_a.png"), pixhash(TMP / "_fp_b.png")
            if ha and hb and ha != hb:
                parts.append("art")
            if pa and pb and pa != pb:
                parts.append("pixels")
            row["ok"] = bool(parts)
            row["level"] = "fingerprint"
            row["detail"] = ("changed: " + ", ".join(parts)) if parts else "no change detected"
    except Exception as e:  # noqa: BLE001
        row["detail"] = f"error: {str(e)[:220]}"
        row["fault"] = ai_run.is_fault(e)
    finally:
        time.sleep(1.2)                                   # dialogs that open after the command returned (e.g. "Replace file?")
        if ai_dialogs.dialogs():
            row["late_dialogs"] = [t for _, _, t in ai_dialogs.dialogs()]
            ai_dialogs.answer_all("esc", 2)
        if c.get("clip"):
            clip_set(clipsave)
    return row


def settle():
    for _ in range(3):
        if not ai_dialogs.dialogs():
            return
        ai_dialogs.answer_all("esc")
        time.sleep(0.6)


def main():
    global rows
    rows = []
    for i, c in enumerate(cases):
        t0 = time.time()
        settle()
        row = run_case(c)
        if row.get("fault") or ("error:" in (row.get("detail") or "") and not ai_run.healthy()) or not ai_run.healthy():
            print("   script engine faulted: restarting Illustrator and retrying once", flush=True)
            ai_run.restart()
            row = run_case(c)
            row["retried"] = True
            if row.get("fault") or ("error:" in (row.get("detail") or "") and not ai_run.healthy()) or not ai_run.healthy():
                ai_run.restart()
        if not row["ok"] and not row.get("retried") and ("check false" in (row.get("detail") or "") or "art hash" in (row.get("detail") or "")):
            # Illustrator occasionally ignores a menu command issued right after the previous one (race inside the app);
            # a second full run (fresh sandbox) must still read the result back positively to pass - no false passes
            settle()
            again = run_case(c)
            if again["ok"]:
                again["retried"] = True
                again["detail"] = (again.get("detail") or "") + " (passed on the 2nd run)"
                row = again
        row["ms"] = int((time.time() - t0) * 1000)
        rows.append(row)
        old[row["cmd"]] = row
        OUT.write_text(json.dumps(list(old.values()), ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{'✅' if row['ok'] else '❌'} {i + 1}/{len(cases)} {c['cmd']:<45} [{row.get('level', '')}] {row.get('detail', '')}", flush=True)
    settle()
    try:
        run_js(PRE + "CLOSEALL(); 'ok'")
    except Exception:  # noqa: BLE001
        pass
    print(f"\n{sum(r['ok'] for r in rows)}/{len(rows)} pass this run; {sum(r['ok'] for r in old.values())}/{len(old)} overall -> tests/menu-sweep.json")



if __name__ == "__main__":
    main()
