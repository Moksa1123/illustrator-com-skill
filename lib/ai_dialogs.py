"""Find and answer Illustrator's modal dialogs (Windows).

Illustrator dialogs are top-level '#32770' windows owned by Illustrator.exe whose content is a custom
Drover view (no standard child buttons), so they are answered with real keystrokes: Enter = OK /
default button, Esc = Cancel. Input goes only to windows that belong to Illustrator.exe.
"""
import ctypes
import time

import psutil
import win32api
import win32con
import win32gui
import win32process

_pid_cache = {}


def _is_ai(h):
    _, pid = win32process.GetWindowThreadProcessId(h)
    if pid not in _pid_cache:
        try:
            _pid_cache[pid] = psutil.Process(pid).name().lower() == "illustrator.exe"
        except Exception:  # noqa: BLE001
            return False
    return _pid_cache[pid]


def windows():
    out = []

    def cb(h, _):
        if win32gui.IsWindowVisible(h) and _is_ai(h):
            out.append((h, win32gui.GetClassName(h), win32gui.GetWindowText(h)))
    win32gui.EnumWindows(cb, None)
    return out


def main_window():
    return next((h for h, c, _ in windows() if c == "illustrator"), None)


DIALOG_CLASSES = {"#32770", "StandardMultiplugin_WindowClass", "PSFilter_WindowClass", "#32768"}


def dialogs():
    """Visible modal dialogs / alerts of Illustrator. Standard dialogs are '#32770', Photoshop-filter effects use
    'StandardMultiplugin_WindowClass'; anything else counts only while the main window is disabled (= a modal is up)."""
    ws = windows()
    main = next((h for h, c, _ in ws if c == "illustrator"), None)
    modal = main is not None and not win32gui.IsWindowEnabled(main)
    return [(h, c, t) for h, c, t in ws if c in DIALOG_CLASSES or (modal and c != "illustrator" and t and not c.startswith("OWL.")
                                                                    and "SplashKit" not in c)]


def _focus(h):
    try:
        import sys as _s
        from pathlib import Path as _P
        _s.path.insert(0, str(_P(__file__).resolve().parent.parent / "tools"))
        import ui_drive as _u
        if _u.focus_window(h):
            return True
    except Exception:  # noqa: BLE001
        pass
    try:
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)          # ALT trick lets SetForegroundWindow succeed
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32gui.SetForegroundWindow(h)
    except Exception:  # noqa: BLE001
        pass
    time.sleep(0.15)
    return win32gui.GetForegroundWindow() == h


OK_TEXT = {"確定", "确定", "OK", "Ok", "好", "はい", "확인", "Yes", "是", "是(Y)", "確定(O)", "OK(O)", "開啟(O)", "開啟", "Open", "儲存(S)", "儲存", "Save", "取代", "Replace", "回復", "Revert", "回復(R)"}
CANCEL_TEXT = {"取消", "Cancel", "キャンセル", "취소", "No", "否", "否(N)", "取消(C)"}


def _button(h, texts):
    hit = []

    def cb(k, _):
        if win32gui.GetClassName(k) == "Button" and win32gui.GetWindowText(k).replace("&", "") in texts and win32gui.IsWindowVisible(k):
            hit.append(k)
    try:
        win32gui.EnumChildWindows(h, cb, None)
    except Exception:  # noqa: BLE001
        pass
    return hit[0] if hit else None


def _uia_click(h, texts):
    """Drover dialogs draw their own buttons (no Win32 children), but UI Automation exposes them with exact
    rectangles. Click the first button whose name is in texts; only while that dialog is the foreground window."""
    try:
        from pywinauto import Desktop
        w = Desktop(backend="uia").window(handle=h)
        for c in w.descendants(control_type="Button"):
            if c.element_info.name.replace("&", "") in texts:
                r = c.element_info.rectangle
                if not (win32gui.GetForegroundWindow() == h or _focus(h)) or win32gui.GetForegroundWindow() != h:
                    return False
                win32api.SetCursorPos(((r.left + r.right) // 2, (r.top + r.bottom) // 2))
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                return True
    except Exception:  # noqa: BLE001
        pass
    return False


def press(h, key="enter"):
    """Answer a dialog: a real OK/Cancel button is clicked (BM_CLICK), otherwise Enter/Esc is typed into it."""
    if not win32gui.IsWindow(h):
        return False
    if key in ("enter", "esc"):
        b = _button(h, OK_TEXT if key == "enter" else CANCEL_TEXT)
        if b:
            win32gui.PostMessage(b, win32con.BM_CLICK, 0, 0)
            return True
        if win32gui.GetClassName(h) == "#32770" and _uia_click(h, OK_TEXT if key == "enter" else CANCEL_TEXT):
            return True
    vk = {"enter": win32con.VK_RETURN, "esc": win32con.VK_ESCAPE, "tab": win32con.VK_TAB, "space": win32con.VK_SPACE}[key]
    if not win32gui.IsWindow(h) or not _focus(h):
        return False
    if win32gui.GetForegroundWindow() != h:              # only ever type into that exact dialog
        return False
    win32api.keybd_event(vk, 0, 0, 0)
    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)
    return True


class _KI(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("extra", ctypes.c_void_p)]


class _INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ki", _KI), ("pad", ctypes.c_ubyte * 8)]


def _key(vk, up=False):
    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP if up else 0, 0)


def steps(h, plan):
    """Drive one dialog with a small plan: 'tab', 'shift+tab', 'enter', 'esc', 'space', 'sel' (Ctrl+A), 'type:text',
    'wait:0.5', 'down', 'up'. Every keystroke is sent only while that dialog is the foreground window."""
    VK = {"tab": win32con.VK_TAB, "enter": win32con.VK_RETURN, "esc": win32con.VK_ESCAPE, "space": win32con.VK_SPACE,
          "down": win32con.VK_DOWN, "up": win32con.VK_UP, "left": win32con.VK_LEFT, "right": win32con.VK_RIGHT, "home": win32con.VK_HOME,
          "end": win32con.VK_END, "del": win32con.VK_DELETE, "back": win32con.VK_BACK}
    for st in plan:
        if st.startswith("wait:"):
            time.sleep(float(st[5:]))
            continue
        if st.startswith("uia:"):                         # uia:<n>:<value> -> set the n-th Edit (UI Automation order) without keyboard focus
            _, n, text = st.split(":", 2)
            try:
                from pywinauto import Desktop
                eds = [x for x in Desktop(backend="uia").window(handle=h).descendants(control_type="Edit")]
                eds[int(n)].iface_value.SetValue(text)
            except Exception:  # noqa: BLE001
                pass
            time.sleep(0.2)
            continue
        if st.startswith("uiasel:") or st.startswith("uiaclick:"):   # select a radio / toggle a checkbox by its label (UIA); uiaclick = real click
            want = st.split(":", 1)[1]
            force = st.startswith("uiaclick:")
            try:
                from pywinauto import Desktop
                for x in Desktop(backend="uia").window(handle=h).descendants():
                    ei = x.element_info
                    if ei.control_type in ("RadioButton", "CheckBox", "Button", "ListItem") and ei.name.replace("&", "").startswith(want):
                        try:
                            if force:
                                raise RuntimeError
                            x.select() if ei.control_type == "RadioButton" else x.toggle()
                        except Exception:  # noqa: BLE001
                            r = ei.rectangle
                            if win32gui.GetForegroundWindow() == h or _focus(h):
                                win32api.SetCursorPos(((r.left + r.right) // 2, (r.top + r.bottom) // 2))
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
                        break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(0.2)
            continue
        if st.startswith("clickrel:"):                    # clickrel:<dx>:<dy> -> click relative to the dialog (dx < 0: from the right edge)
            _, dx, dy = st.split(":")
            if (win32gui.GetForegroundWindow() == h or _focus(h)) and win32gui.GetForegroundWindow() == h:
                l, t, r, b = win32gui.GetWindowRect(h)
                x = (r + int(dx)) if int(dx) < 0 else (l + int(dx))
                win32api.SetCursorPos((x, t + int(dy)))
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            time.sleep(0.2)
            continue
        if st.startswith("clickedit:") or st.startswith("click:"):   # clickedit:<n> / click:<Class>:<n> -> click the n-th visible control
            cls, n = ("Edit", st.split(":")[1]) if st.startswith("clickedit:") else st.split(":")[1:3]
            n = int(n)
            eds = []
            win32gui.EnumChildWindows(h, lambda k, _: eds.append(k) if win32gui.GetClassName(k) == cls and win32gui.IsWindowVisible(k) else None, None)
            if n < len(eds) and (win32gui.GetForegroundWindow() == h or _focus(h)) and win32gui.GetForegroundWindow() == h:
                l, t, r, b = win32gui.GetWindowRect(eds[n])
                win32api.SetCursorPos(((l + r) // 2, (t + b) // 2))
                time.sleep(0.05)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            time.sleep(0.2)
            continue
        if st.startswith("editval:"):                     # editval:<current>:<new> -> the Edit control showing <current> gets <new>
            _, cur, text = st.split(":", 2)
            eds = []
            win32gui.EnumChildWindows(h, lambda k, _: eds.append(k) if win32gui.GetClassName(k) == "Edit" and win32gui.IsWindowVisible(k) else None, None)
            for k in eds:
                if win32gui.GetWindowText(k).strip() == cur:
                    win32gui.SendMessage(k, win32con.WM_SETTEXT, 0, text)
                    win32gui.SendMessage(h, win32con.WM_COMMAND, (0x0300 << 16) | win32gui.GetDlgCtrlID(k), k)
                    break
            time.sleep(0.2)
            continue
        if st.startswith("edit:"):                        # edit:<n>:<text> -> WM_SETTEXT on the n-th Edit control
            _, n, text = st.split(":", 2)
            eds = []
            win32gui.EnumChildWindows(h, lambda k, _: eds.append(k) if win32gui.GetClassName(k) == "Edit" and win32gui.IsWindowVisible(k) else None, None)
            if int(n) < len(eds):
                win32gui.SendMessage(eds[int(n)], win32con.WM_SETTEXT, 0, text)
                win32gui.SendMessage(h, win32con.WM_COMMAND, (0x0300 << 16) | win32gui.GetDlgCtrlID(eds[int(n)]), eds[int(n)])  # EN_CHANGE
            time.sleep(0.2)
            continue
        if st == "ok" or st == "cancel":
            b = _button(h, OK_TEXT if st == "ok" else CANCEL_TEXT)
            if b:
                win32gui.PostMessage(b, win32con.BM_CLICK, 0, 0)
                continue
            if _uia_click(h, OK_TEXT if st == "ok" else CANCEL_TEXT):
                time.sleep(0.2)
                continue
            st = "enter" if st == "ok" else "esc"
        if not win32gui.IsWindow(h) or (win32gui.GetForegroundWindow() != h and not _focus(h)):
            return False
        if win32gui.GetForegroundWindow() != h:
            return False
        if st.startswith("type:"):
            for ch in st[5:]:
                for flag in (0, 2):
                    x = _INPUT(1, _KI(0, ord(ch), 4 | flag, 0, None))
                    ctypes.windll.user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
                time.sleep(0.01)
        elif st == "sel":
            _key(win32con.VK_CONTROL); _key(ord("A")); _key(ord("A"), True); _key(win32con.VK_CONTROL, True)
        elif st == "shift+tab":
            _key(win32con.VK_SHIFT); _key(win32con.VK_TAB); _key(win32con.VK_TAB, True); _key(win32con.VK_SHIFT, True)
        else:
            _key(VK[st]); _key(VK[st], True)
        time.sleep(0.12)
    return True


def answer_all(key="enter", rounds=1):
    n = 0
    for _ in range(rounds):
        for h, _, _ in dialogs():
            n += press(h, key)
        time.sleep(0.3)
    return n


ctypes.windll.user32.SetProcessDPIAware()
