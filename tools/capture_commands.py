"""Capture YOUR Illustrator's full menu-command inventory (then run index/build_menu_index.py).

Illustrator has no scriptable menu tree. Edit > Keyboard Shortcuts can Save the current set as a .kys file that lists
the internal name of every menu command (= the string app.executeMenuCommand takes), and Export Text writes the
localized menu. This tool opens that dialog with executeMenuCommand('KBSC Menu Item'), clicks Save / Export Text,
types the file names, cancels the dialog, and moves the saved set out of your settings folder again.
Only Illustrator windows ever receive input (lib/ai_dialogs.py, tools/ui_drive.py).
Output: index/raw/ai<version>_commands.kys, index/raw/shortcuts_<locale>.txt
Usage:  python tools/capture_commands.py
"""
import os
import shutil
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

RAW = SKILL / "index" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
# button positions as fractions of the Keyboard Shortcuts dialog (measured on Illustrator 28, any DPI)
SAVE_ICON = (0.873, 0.099)
EXPORT_TEXT = (0.153, 0.924)


def wait_dialog(title_not=None, timeout=15):
    t0 = time.time()
    while time.time() - t0 < timeout:
        d = [x for x in ai_dialogs.dialogs() if x[1] == "#32770" and x[2] != title_not]
        if d:
            return d[0]
        time.sleep(0.3)
    raise SystemExit("dialog did not open")


def click_frac(h, fx, fy):
    l, t, r, b = win32gui.GetWindowRect(h)
    ui_drive.focus_window(h)
    ui_drive.click(int(l + (r - l) * fx), int(t + (b - t) * fy))


def main():
    ver = run_js("app.version").split(".")[0]
    loc = run_js("app.locale")
    th = threading.Thread(target=lambda: run_js("app.executeMenuCommand('KBSC Menu Item'); 'closed'", dialog=None, timeout=900), daemon=True)
    th.start()
    kb = wait_dialog()
    time.sleep(1)
    # 1. Export Text
    click_frac(kb[0], *EXPORT_TEXT)
    time.sleep(1.5)
    txt = RAW / f"shortcuts_{loc}.txt"
    txt.unlink(missing_ok=True)
    ui_drive.key(ord("A"), [0x11])
    ui_drive.type_text(str(txt))
    ui_drive.enter()
    time.sleep(2)
    # 2. Save the set under a temporary name
    click_frac(kb[0], *SAVE_ICON)
    time.sleep(1.5)
    name = "ai_skill_capture"
    ui_drive.key(ord("A"), [0x11])
    ui_drive.type_text(name)
    ui_drive.enter()
    time.sleep(2)
    # 3. Cancel the dialog so the user's active set is unchanged
    ai_dialogs.answer_all("esc", 2)
    th.join(20)
    settings = Path(os.environ["APPDATA"]) / "Adobe"
    hits = list(settings.glob(f"Adobe Illustrator {ver} Settings/*/*/{name}.kys")) + list(settings.glob(f"Adobe Illustrator {ver} Settings/*/{name}.kys"))
    if not hits:
        raise SystemExit("saved set not found in the settings folder")
    dst = RAW / f"ai{2024 if ver == '28' else ver}_commands.kys"
    shutil.copy(hits[0], dst)
    hits[0].unlink()
    print(f"saved {dst} and {txt}; now run: python index/build_menu_index.py")


if __name__ == "__main__":
    main()
