"""Illustrator window input (screenshot + keyboard/mouse) that only ever targets Illustrator: before any input the foreground window must belong to Illustrator.exe, otherwise it stops.
Use: answer dialogs a command opened, or drive the few features that only exist on screen.
"""
import ctypes
import time
from pathlib import Path

import win32api
import win32con
import win32gui
import win32process
from PIL import ImageGrab

user32 = ctypes.windll.user32


def _exe(hwnd):
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        h = win32api.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        import win32process as wp
        return Path(wp.GetModuleFileNameEx(h, 0)).name.lower()
    except Exception:
        return ""


def ai_windows():
    out = []
    def cb(h, _):
        if win32gui.IsWindowVisible(h) and _exe(h) == "illustrator.exe":
            out.append((h, win32gui.GetWindowText(h), win32gui.GetWindowRect(h)))
    win32gui.EnumWindows(cb, None)
    return out


def activate():
    wins = ai_windows()
    if not wins:
        raise RuntimeError("no Illustrator window")
    fg = win32gui.GetForegroundWindow()
    if _exe(fg) == "illustrator.exe":
        return fg
    main = max(wins, key=lambda w: (w[2][2] - w[2][0]) * (w[2][3] - w[2][1]))[0]
    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)  # tap Alt so SetForegroundWindow is allowed
    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32gui.SetForegroundWindow(main)
    time.sleep(0.4)
    return win32gui.GetForegroundWindow()


def guard():
    fg = win32gui.GetForegroundWindow()
    if _exe(fg) != "illustrator.exe":
        raise RuntimeError(f"foreground window is not Illustrator ({win32gui.GetWindowText(fg)}); input stopped")
    return fg


def key(vk, mods=()):
    guard()
    for m in mods:
        win32api.keybd_event(m, 0, 0, 0)
    win32api.keybd_event(vk, 0, 0, 0)
    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
    for m in reversed(mods):
        win32api.keybd_event(m, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.15)


def enter():
    key(win32con.VK_RETURN)


def esc():
    key(win32con.VK_ESCAPE)


def click(x, y, double=False):
    guard()
    win32api.SetCursorPos((x, y))
    time.sleep(0.05)
    for _ in range(2 if double else 1):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    time.sleep(0.2)


def drag(x1, y1, x2, y2, steps=15):
    guard()
    win32api.SetCursorPos((x1, y1)); time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    for i in range(1, steps + 1):
        win32api.SetCursorPos((x1 + (x2 - x1) * i // steps, y1 + (y2 - y1) * i // steps)); time.sleep(0.02)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    time.sleep(0.2)


def shot(path, box=None):
    img = ImageGrab.grab(bbox=box, all_screens=True)
    img.save(path)
    return path


def fg_info():
    fg = win32gui.GetForegroundWindow()
    return _exe(fg), win32gui.GetWindowText(fg), win32gui.GetWindowRect(fg)


def type_text(t):
    """Send Unicode characters one by one (works for CJK and paths, no clipboard)."""
    guard()

    class KI(ctypes.Structure):
        _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("extra", ctypes.c_void_p)]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong), ("ki", KI), ("pad", ctypes.c_ubyte * 8)]
    for ch in t:
        for flag in (0, 2):
            x = INPUT(1, KI(0, ord(ch), 4 | flag, 0, None))
            user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
        time.sleep(0.01)


def focus_window(h):
    """Bring an Illustrator window to the front. Windows refuses SetForegroundWindow from a background process, so the
    input queue of the current foreground thread is attached for the call (standard workaround)."""
    for attempt in range(3):
        fg = win32gui.GetForegroundWindow()
        if fg == h:
            return True
        cur = win32api.GetCurrentThreadId()
        other = win32process.GetWindowThreadProcessId(fg)[0] if fg else 0
        try:
            if other and other != cur:
                user32.AttachThreadInput(other, cur, True)
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            if win32gui.IsIconic(h):
                win32gui.ShowWindow(h, win32con.SW_RESTORE)
            flags = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            win32gui.SetWindowPos(h, win32con.HWND_TOPMOST, 0, 0, 0, 0, flags)       # lift above other apps' windows...
            win32gui.SetWindowPos(h, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, flags)     # ...without staying always-on-top
            win32gui.BringWindowToTop(h)
            win32gui.SetForegroundWindow(h)
        except Exception:  # noqa: BLE001
            pass
        finally:
            if other and other != cur:
                user32.AttachThreadInput(other, cur, False)
        time.sleep(0.3)
    if win32gui.IsWindow(h) and win32gui.GetForegroundWindow() != h and win32gui.GetClassName(h) == "illustrator":
        placement = win32gui.GetWindowPlacement(h)[1]            # last resort: minimize + restore our own window
        win32gui.ShowWindow(h, win32con.SW_MINIMIZE)
        time.sleep(0.3)
        win32gui.ShowWindow(h, win32con.SW_MAXIMIZE if placement == win32con.SW_SHOWMAXIMIZED else win32con.SW_RESTORE)
        time.sleep(0.8)
        try:
            win32gui.SetForegroundWindow(h)
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.3)
    if win32gui.IsWindow(h) and win32gui.GetForegroundWindow() != h:
        l, t, r, b = win32gui.GetWindowRect(h)                    # click an empty spot of its own title bar
        x, y = (l + r) // 2 + 200, max(t, 0) + 6
        at = win32gui.WindowFromPoint((x, y))
        if at and win32gui.GetAncestor(at, 2) == h:               # GA_ROOT: the point really belongs to this window
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            time.sleep(0.4)
    if win32gui.IsWindow(h) and win32gui.GetForegroundWindow() != h:
        try:                                                        # the taskbar button: a switch Windows always honours
            from pywinauto import Desktop
            tb = Desktop(backend="uia").window(class_name="Shell_TrayWnd")
            for btn in tb.descendants(control_type="Button"):
                if (btn.element_info.name or "").startswith("Adobe Illustrator"):
                    r = btn.element_info.rectangle
                    win32api.SetCursorPos(((r.left + r.right) // 2, (r.top + r.bottom) // 2))
                    time.sleep(0.1)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                    time.sleep(0.8)
                    break
        except Exception:  # noqa: BLE001
            pass
    return win32gui.GetForegroundWindow() == h


user32.SetProcessDPIAware()
