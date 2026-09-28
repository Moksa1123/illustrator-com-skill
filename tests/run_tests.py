"""Run the ailib tests: each test executes in an Illustrator sandbox document and reads its result back.
Beyond the JS-side asserts, this runner checks what ExtendScript cannot see:
  px    exports the artboard to PNG (1 px = 1 pt) and samples pixels
  fx    saves an uncompressed .ai and requires the listed live effects (tools/ai_dump.py)
  files each exported file must exist, be non-empty and (for images) decode; `size` checks pixel dimensions
Output: tests/report.json, tests/REPORT.md, tests/snaps/<n>.png
Usage:  python tests/run_tests.py [--only words]
"""
import argparse
import datetime
import json
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL / "lib"))
sys.path.insert(0, str(SKILL / "tools"))
sys.stdout.reconfigure(encoding="utf-8")
import ai_dump  # noqa: E402
import ai_run  # noqa: E402
from ai_run import run_js  # noqa: E402
from ailib_loader import library  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--only")
a = ap.parse_args()
snap = HERE / "snaps"
snap.mkdir(exist_ok=True)
SRC = library() + (HERE / "sandbox.jsx").read_text(encoding="utf-8") + (HERE / "tests.jsx").read_text(encoding="utf-8")
TMP = Path(run_js(SRC + "Folder(TMP).fsName"))
tests = json.loads(run_js(SRC + "J(listTests())"))
if a.only:
    tests = [t for t in tests if all(w.lower() in (t["cat"] + " " + t["name"]).lower() for w in a.only.split())]


def post(r, i):
    """Python-side readback checks."""
    notes = []
    if r.get("px") is not None or r.get("fx"):
        png = snap / f"{i:02d}.png"
        run_js(SRC + f"PNG({json.dumps(str(png).replace(chr(92), '/'))}, 100); 'ok'")
        im = Image.open(png).convert("RGB")
        for x, y, rgb, tol in r.get("px") or []:
            got = im.getpixel((min(int(x), im.width - 1), min(int(y), im.height - 1)))
            if max(abs(got[k] - rgb[k]) for k in range(3)) > tol:
                raise AssertionError(f"pixel ({x},{y}) = {got}, expected {rgb} ±{tol}")
        if r.get("px"):
            notes.append(f"{len(r['px'])} pixels sampled")
    else:
        run_js(SRC + f"PNG({json.dumps(str(snap / f'{i:02d}.png').replace(chr(92), '/'))}, 100); 'ok'")
    if r.get("fx"):
        f = TMP / f"_t{i}.ai"
        run_js(SRC + f"SAVEAI({json.dumps(str(f).replace(chr(92), '/'))}); 'ok'")
        names = [e["name"] for e in ai_dump.effects(f)]
        miss = [n for n in r["fx"] if n not in names]
        if miss:
            raise AssertionError(f"live effects missing from the saved file: {miss}")
        notes.append("effects read back: " + ", ".join(r["fx"]))
    for k, f in enumerate(r.get("files") or []):
        p = Path(f)
        if not p.exists() or p.stat().st_size == 0:
            raise AssertionError(f"missing or empty: {p.name}")
        if p.suffix.lower() in (".png", ".jpg", ".webp"):
            im = Image.open(p)
            im.load()
            want = (r.get("size") or {}).get({0: "png", 1: "png2"}.get(k, ""), None)
            if want and list(im.size) != want:
                raise AssertionError(f"{p.name} is {im.size}, expected {want}")
        if p.suffix.lower() == ".svg" and b"<svg" not in p.read_bytes()[:2000]:
            raise AssertionError(f"{p.name} is not SVG")
        if p.suffix.lower() == ".psd" and p.read_bytes()[:4] != b"8BPS":
            raise AssertionError(f"{p.name} is not PSD")
        if p.suffix.lower() == ".pdf" and p.read_bytes()[:5] != b"%PDF-":
            raise AssertionError(f"{p.name} is not PDF")
    if r.get("files"):
        notes.append(f"{len(r['files'])} files decoded")
    return notes


def attempt(t):
    try:
        r = json.loads(run_js(SRC + f"J(runOne({t['i']}))", dialog="enter", timeout=300))
    except Exception as e:  # noqa: BLE001
        r = {"ok": False, "msg": f"error: {str(e)[:200]}", "cat": t["cat"], "name": t["name"], "ms": 0, "fault": ai_run.is_fault(e)}
        if ai_run.is_fault(e) or not ai_run.healthy():
            ai_run.restart()
        return r
    if r.get("ok"):
        try:
            notes = post(r, t["i"])
            if notes:
                r["msg"] += " | " + "; ".join(notes)
        except Exception as e:  # noqa: BLE001
            r["ok"] = False
            r["msg"] += f" | FAILED readback: {e}"
            r["fault"] = ai_run.is_fault(e)
            if r["fault"]:
                ai_run.restart()
    return r


results = []
for t in tests:
    r = attempt(t)
    if not r["ok"] and r.get("fault"):          # the script engine faulted (RPC_E_SERVERFAULT), not the test: run it once more
        r = attempt(t)
        r["msg"] += " (retried after an engine fault)"
    r.pop("fault", None)
    results.append(r)
    print(("✅" if r["ok"] else "❌"), r["cat"], "|", r["name"], "|", r["msg"], flush=True)
try:
    run_js(SRC + "CLOSEALL(); 'ok'")
except Exception:  # noqa: BLE001
    pass

rep = {"version": run_js("app.version"), "date": datetime.datetime.now().isoformat(timespec="seconds"), "results": results}
old = HERE / "report.json"
if a.only and old.exists():
    prev = {(x["cat"], x["name"]): x for x in json.loads(old.read_text(encoding="utf-8"))["results"]}
    prev.update({(x["cat"], x["name"]): x for x in results})
    rep["results"] = list(prev.values())
def _anon(o):                                   # the sandbox folder path contains the user name: store it as <sandbox>
    if isinstance(o, str):
        return o.replace(str(TMP), "<sandbox>").replace(TMP.as_posix(), "<sandbox>")
    if isinstance(o, list):
        return [_anon(x) for x in o]
    if isinstance(o, dict):
        return {k: _anon(v) for k, v in o.items()}
    return o


rep = _anon(rep)
old.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
n_ok = sum(x["ok"] for x in rep["results"])
lines = ["# ailib test report", "", f"- Illustrator {rep['version']} | {rep['date']} | **{n_ok}/{len(rep['results'])} pass**", "",
         "| Area | Function | Result | Read back |", "|---|---|---|---|"]
for x in rep["results"]:
    lines.append(f"| {x['cat']} | {x['name']} | {'✅' if x['ok'] else '❌'} | {x['msg'].replace('|', '/')} |")
lines += ["", "Only ✅ functions are for production use. Snapshots of every test document: tests/snaps/."]
(HERE / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"\n{n_ok}/{len(rep['results'])} pass -> tests/REPORT.md")
