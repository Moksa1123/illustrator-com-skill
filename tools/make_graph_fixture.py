"""Make tests/fixtures/graph.ai: a column graph drawn with the Column Graph tool.
Illustrator's DOM can read and restyle graphs (GraphItem) but cannot create one, so the menu sweep's Graph cases
start from this fixture. The tool is selected by script (app.selectTool), one click lands in the middle of the
document window, the Graph size dialog is accepted, and the graph data window is closed.
Usage: python tools/make_graph_fixture.py
"""
import sys
import threading
import time
from pathlib import Path

import win32gui

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "lib"))
sys.path.insert(0, str(SKILL / "tools"))
import ai_dialogs  # noqa: E402
import ui_drive  # noqa: E402
from ai_run import run_js  # noqa: E402
from ailib_loader import library  # noqa: E402

out = SKILL / "tests" / "fixtures" / "graph.ai"
run_js(library() + "while (app.documents.length) app.documents[0].close(SaveOptions.DONOTSAVECHANGES); AI.newDoc(800, 600, 'graph', {units: 'pt'}); "
       "app.activeDocument.activeView.zoom = 0.5; app.selectTool('Adobe Column Graph Tool'); 'ok'")
main = ai_dialogs.main_window()
l, t, r, b = win32gui.GetWindowRect(main)
ui_drive.focus_window(main)
cx, cy = (l + r) // 2, (t + b) // 2
ui_drive.click(cx, cy)
time.sleep(1.5)
for h, c, title in ai_dialogs.dialogs():
    ai_dialogs.press(h, "enter")
time.sleep(2)
# the graph data window is a floating panel: close it with its own close box via Esc-free path (select tool + script)
n = run_js("app.selectTool('Adobe Select Tool'); app.activeDocument.graphItems.length")
if n == "0":
    raise SystemExit("no graph was created (the click did not land on the canvas?)")
for h, c, title in ai_dialogs.windows():
    if c not in ("illustrator",) and win32gui.IsWindowVisible(h) and "OWL" not in c and "Drover" not in c:
        try:
            win32gui.PostMessage(h, 0x0010, 0, 0)       # WM_CLOSE the data window
        except Exception:  # noqa: BLE001
            pass
time.sleep(1)
out.parent.mkdir(parents=True, exist_ok=True)
print(run_js(f"var o = new IllustratorSaveOptions(); app.activeDocument.saveAs(new File({str(out.as_posix())!r}), o); "
             "var g = app.activeDocument.graphItems[0]; var n = app.activeDocument.graphItems.length; app.activeDocument.close(SaveOptions.DONOTSAVECHANGES); 'graphs: ' + n"))
