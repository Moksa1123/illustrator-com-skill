"""Illustrator screen control from the command line: python tools/ui.py <step>... (steps run in order)
  shot <file>             full-screen screenshot (physical pixels)
  crop <file> x1 y1 x2 y2 screenshot of a region
  click x y / dclick x y  click (physical pixels)
  drag x1 y1 x2 y2        drag
  key enter|esc|tab|f9|alt+f9|ctrl+z|...   key (combine with +)
  type <text>             type Unicode text (no clipboard)
  dialogs                 list open Illustrator dialogs
  wait <seconds>
Before every input Illustrator is brought to the front and the foreground window must belong to Illustrator.exe.
"""
import ctypes
import sys
import time

ctypes.windll.user32.SetProcessDPIAware()
import win32api  # noqa: E402
import win32con  # noqa: E402

import ui_drive  # noqa: E402

VK = {"enter": win32con.VK_RETURN, "esc": win32con.VK_ESCAPE, "tab": win32con.VK_TAB, "space": win32con.VK_SPACE,
      "up": win32con.VK_UP, "down": win32con.VK_DOWN, "left": win32con.VK_LEFT, "right": win32con.VK_RIGHT,
      "del": win32con.VK_DELETE, "back": win32con.VK_BACK, "alt": win32con.VK_MENU, "ctrl": win32con.VK_CONTROL, "shift": win32con.VK_SHIFT}
for i in range(1, 13):
    VK[f"f{i}"] = getattr(win32con, f"VK_F{i}")


def vk(name):
    return VK.get(name) or ord(name.upper())


type_text = ui_drive.type_text


a = sys.argv[1:]
i = 0
while i < len(a):
    c = a[i]
    if c == "shot":
        ui_drive.shot(a[i + 1]); i += 2
    elif c == "crop":
        ui_drive.shot(a[i + 1], tuple(int(v) for v in a[i + 2:i + 6])); i += 6
    elif c in ("click", "dclick"):
        ui_drive.activate(); ui_drive.click(int(a[i + 1]), int(a[i + 2]), double=c == "dclick"); i += 3
    elif c == "drag":
        ui_drive.activate(); ui_drive.drag(*[int(v) for v in a[i + 1:i + 5]]); i += 5
    elif c == "key":
        ui_drive.activate(); parts = a[i + 1].split("+"); ui_drive.key(vk(parts[-1]), [vk(p) for p in parts[:-1]]); i += 2
    elif c == "type":
        ui_drive.activate(); type_text(a[i + 1]); i += 2
    elif c == "wait":
        time.sleep(float(a[i + 1])); i += 2
    elif c == "dialogs":
        sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent / "lib"))
        import ai_dialogs
        print(ai_dialogs.dialogs()); i += 1
    else:
        raise SystemExit(f"unknown step: {c}")
    time.sleep(0.3)
print("foreground:", ui_drive.fg_info()[1])
