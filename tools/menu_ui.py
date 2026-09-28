import os
"""Run a menu command the way a user does: through Illustrator's real menu bar.

A handful of commands refuse app.executeMenuCommand (it throws PARM, the same as for an unknown name) although the
menu item is enabled — e.g. Type > Type on a Path > Rainbow. Illustrator's popup menus are native Win32 menus
(#32768), so each level can be READ (labels, enabled state) and walked with the keyboard:
  Alt+<access key> opens the top menu; at every level the item is found by its label, arrow keys move to it
  (separators are skipped), Right opens a submenu, Enter runs the item. Keys go only to Illustrator (foreground check).

    from menu_ui import menu_click, menu_list
    menu_click(["文字", "路徑文字", "彩虹效果"])       # labels as shown in YOUR Illustrator's language
    menu_list(["物件", "路徑"])                         # [(label, enabled), ...]

CLI: python tools/menu_ui.py 文字 路徑文字 彩虹效果    |    python tools/menu_ui.py --list 物件 路徑
"""
import ctypes
import re
import sys
import time
from pathlib import Path

import win32con
import win32gui

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "lib"))
sys.path.insert(0, str(SKILL / "tools"))
import ai_dialogs  # noqa: E402
import ui_drive  # noqa: E402

U = ctypes.windll.user32
MN_GETHMENU = 0x01E1
TOP_KEYS = {"檔案": "F", "編輯": "E", "物件": "O", "文字": "T", "選取": "S", "效果": "C", "檢視": "V", "視窗": "W", "說明": "H",
            "File": "F", "Edit": "E", "Object": "O", "Type": "T", "Select": "S", "Effect": "C", "View": "V", "Window": "W", "Help": "H"}


def _clean(s):
    return re.sub(r"\(&.\)|&|\x08.*$|\.\.\.$|…$", "", s).strip()


def popups():
    return [h for h, c, _ in ai_dialogs.windows() if c == "#32768"]


def items(h):
    hm = win32gui.SendMessage(h, MN_GETHMENU, 0, 0)
    out = []
    for i in range(U.GetMenuItemCount(hm)):
        buf = ctypes.create_unicode_buffer(256)
        U.GetMenuStringW(hm, i, buf, 256, 0x400)
        st = U.GetMenuState(hm, i, 0x400)
        m = re.search(r"&(\w)", buf.value)
        out.append({"clean": _clean(buf.value), "sep": not buf.value, "enabled": not (st & 3), "sub": bool(st & 0x10),
                    "key": m.group(1).upper() if m else None})
    return out


def _key(vk, mods=()):
    ui_drive.guard()
    ui_drive.key(vk, list(mods))
    time.sleep(0.12)


def close_menus():
    for _ in range(5):
        if not popups():
            return
        try:
            _key(win32con.VK_ESCAPE)
        except RuntimeError:
            return


def _wait_new(before, timeout=2.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        new = [p for p in popups() if p not in before]
        if new:
            return new[-1]
        time.sleep(0.05)
    raise RuntimeError("menu did not open")


class _RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def _item_rect(h, i):
    hm = win32gui.SendMessage(h, MN_GETHMENU, 0, 0)
    r = _RECT()
    if not U.GetMenuItemRect(None, hm, i, ctypes.byref(r)):
        return None
    return r.left, r.top, r.right, r.bottom


def _click(x, y):
    ui_drive.guard()
    ui_drive.click(x, y)
    time.sleep(0.15)


def _walk(path):
    """Open the top menu with Alt+key, then CLICK each item at the rectangle the native menu reports for it."""
    close_menus()
    main = ai_dialogs.main_window()
    ui_drive.focus_window(main)
    time.sleep(0.3)
    before = set(popups())
    _key(ord(TOP_KEYS[path[0]]), [win32con.VK_MENU])
    h = _wait_new(before)
    for want in path[1:]:
        its = items(h)
        idx = next((i for i, it in enumerate(its) if not it["sep"] and (it["clean"] == _clean(want) or it["clean"].startswith(_clean(want)))), None)
        if idx is None:
            raise RuntimeError(f"'{want}' not in menu: {[it['clean'] for it in its if not it['sep']]}")
        rc = _item_rect(h, idx)
        if not rc:
            raise RuntimeError(f"no rectangle for '{want}'")
        yield h, its[idx], rc
        if its[idx]["sub"]:
            before = set(popups())
            ui_drive.guard()
            import win32api
            win32api.SetCursorPos(((rc[0] + rc[2]) // 2, (rc[1] + rc[3]) // 2))   # hovering opens the submenu
            time.sleep(0.5)
            try:
                h = _wait_new(before, 1.5)
            except RuntimeError:
                _click((rc[0] + rc[2]) // 2, (rc[1] + rc[3]) // 2)
                h = _wait_new(before)
    yield h, None, None


def menu_list(path):
    """Labels and enabled state of the menu at path (e.g. ['物件', '路徑'])."""
    try:
        h = None
        for h, it, rc in _walk(path):
            pass
        return [(it["clean"], it["enabled"]) for it in items(h) if not it["sep"]]
    finally:
        close_menus()


def menu_click(path):
    """Run the item at path; raises if it is missing or disabled."""
    try:
        for h, it, rc in _walk(path):
            if it is None:
                raise RuntimeError("path ends in a submenu")
            if it is not None and not it["sub"]:
                if not it["enabled"]:
                    raise RuntimeError(f"'{it['clean']}' is disabled in the current context")
                _click((rc[0] + rc[2]) // 2, (rc[1] + rc[3]) // 2)
                return True
    finally:
        if popups():
            close_menus()


# ── on-canvas widgets (AI 2024 Simplify / Smooth): no window of their own, so find them on screen ──────────────────
WIDGET_GRAY = (83, 83, 83)


def widget_rect():
    """Screen rectangle of the floating on-canvas widget: a solid dark-gray bar 240-330 px wide and 35-70 px tall,
    outside every Illustrator panel window."""
    from PIL import ImageGrab
    panels = [win32gui.GetWindowRect(h) for h, c, _ in ai_dialogs.windows() if c != "illustrator"]
    im = ImageGrab.grab(all_screens=True).convert("RGB")
    W, H = im.size
    px = im.load()
    rows = []
    for y in range(80, H - 80, 2):
        x = 60
        while x < W - 60:
            if px[x, y] == WIDGET_GRAY:
                s = x
                while x < W - 60 and px[x, y] == WIDGET_GRAY:
                    x += 1
                if 240 <= x - s <= 330 and not any(l <= s <= r and t <= y <= b for l, t, r, b in panels):
                    rows.append((y, s, x))
            x += 1
    clusters = []   # one open cluster per column: other gray bars (panels) interleave by y
    for r in rows:
        for c in clusters:
            if abs(r[1] - c[-1][1]) <= 20 and r[0] - c[-1][0] <= 30:   # icons interrupt the middle rows: allow gaps
                c.append(r)
                break
        else:
            clusters.append([r])
    good = [c for c in clusters if 35 <= c[-1][0] - c[0][0] + 2 <= 70]
    if not good:
        raise RuntimeError("no on-canvas widget found")
    c = good[0]
    return min(r[1] for r in c), c[0][0], max(r[2] for r in c), c[-1][0]


def widget_drag(dx, knob_offset=64):
    """Drag the widget's slider knob (at the left end of its track) dx pixels to the right; releasing applies it."""
    l, t, r, b = widget_rect()
    y = (t + b) // 2
    ui_drive.guard()
    ui_drive.drag(l + knob_offset, y, l + knob_offset + dx, y)
    time.sleep(0.8)
    return l, t, r, b


def menu_checked(path):
    """True if the menu item at path shows a checkmark (MF_CHECKED): readback for toggles such as View > Guides > Lock Guides."""
    try:
        h = None
        for h, it, rc in _walk(path[:-1]):
            pass
        hm = win32gui.SendMessage(h, MN_GETHMENU, 0, 0)
        for i in range(U.GetMenuItemCount(hm)):
            buf = ctypes.create_unicode_buffer(256)
            U.GetMenuStringW(hm, i, buf, 256, 0x400)
            if _clean(buf.value) == _clean(path[-1]) or _clean(buf.value).startswith(_clean(path[-1])):
                return bool(U.GetMenuState(hm, i, 0x400) & 0x8)
        raise RuntimeError(f"'{path[-1]}' not found")
    finally:
        close_menus()


def _retry(fn):
    def wrapped(*a, **k):
        for attempt in range(4):
            try:
                return fn(*a, **k)
            except RuntimeError as e:
                if attempt == 3 or not any(x in str(e) for x in ("foreground", "did not open")):
                    raise
                close_menus() if ui_drive.focus_window(ai_dialogs.main_window()) else None
                time.sleep(1.5)
    return wrapped


menu_list = _retry(menu_list)
menu_click = _retry(menu_click)
menu_checked = _retry(menu_checked)



def color_bbox(rgb, tol=6):
    """Screen box (l, t, r, b) of all pixels of colour rgb inside Illustrator's main window (artwork on the canvas)."""
    from PIL import ImageGrab
    main = ai_dialogs.main_window()
    l, t, r, b = win32gui.GetWindowRect(main)
    ox, oy = max(l, 0) + 60, max(t, 0) + 120
    im = ImageGrab.grab(bbox=(ox, oy, r - 360, b - 60), all_screens=True).convert("RGB")
    px = im.load()
    xs, ys = [], []
    for y in range(0, im.size[1], 2):
        for x in range(0, im.size[0], 2):
            p = px[x, y]
            if all(abs(p[k] - rgb[k]) <= tol for k in range(3)):
                xs.append(x)
                ys.append(y)
    if len(xs) < 100:
        im.save(os.path.join(os.environ.get("TEMP", "."), "_color_bbox_fail.png"))
        raise RuntimeError(f"colour {rgb} not on screen")
    return ox + min(xs), oy + min(ys), ox + max(xs), oy + max(ys)


def edge_drag(rgb, frac):
    """Drag the right-middle handle of the artwork of colour rgb (a crop / bounding-box handle) left by frac of its width."""
    ui_drive.focus_window(ai_dialogs.main_window())
    l, t, r, b = color_bbox(rgb)
    y = (t + b) // 2
    ui_drive.guard()
    ui_drive.drag(r + 1, y, r + 1 - int((r - l) * frac), y)
    time.sleep(0.8)

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "--list":
        for label, on in menu_list(sys.argv[2:]):
            print(label + ("" if on else "  (disabled)"))
    else:
        print(menu_click(sys.argv[1:]))


def find_color(rgb, tol=6):
    """Screen point of the first pixel of colour rgb inside Illustrator's main window (to click artwork)."""
    from PIL import ImageGrab
    main = ai_dialogs.main_window()
    l, t, r, b = win32gui.GetWindowRect(main)
    im = ImageGrab.grab(bbox=(max(l, 0) + 60, max(t, 0) + 120, r - 360, b - 60), all_screens=True).convert("RGB")
    px = im.load()
    for y in range(0, im.size[1], 3):
        for x in range(0, im.size[0], 3):
            p = px[x, y]
            if all(abs(p[k] - rgb[k]) <= tol for k in range(3)) and x + 20 < im.size[0] and y + 20 < im.size[1] and all(
                    all(abs(px[x + dx, y + dy][k] - rgb[k]) <= tol for k in range(3)) for dx in (0, 10, 20) for dy in (0, 10, 20)):
                return max(l, 0) + 60 + x + 10, max(t, 0) + 120 + y + 10     # a solid 20x20 block: artwork, not an icon
    raise RuntimeError(f"colour {rgb} not on screen")


def dblclick_color(rgb):
    ui_drive.focus_window(ai_dialogs.main_window())
    x, y = find_color(rgb)
    ui_drive.guard()
    ui_drive.click(x, y, double=True)
    time.sleep(0.8)
    return x, y
