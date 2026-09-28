"""Run ExtendScript in Adobe Illustrator over COM and return the result string.

Illustrator's COM type library is often unregistered (TYPE_E_LIBNOTREGISTERED), which breaks PowerShell and
win32com early binding. We call IDispatch::GetIDsOfNames("DoJavaScript") + Invoke directly, so no type library
is needed and no "run this script?" dialog ever appears (that only happens for File > Scripts / Illustrator.exe x.jsx).

Dialog watchdog: the script runs in a worker thread while this thread watches for Illustrator modal dialogs
(many menu commands open one, and a dialog blocks the COM call forever):
  dialog="esc"   (default) cancel any dialog, so a script can never hang Illustrator
  dialog="enter" accept every dialog with its current values (used to run dialog-only commands with defaults)
  dialog=[...]   fill in the first dialog with a plan such as ["sel", "type:45", "tab", "ok"], accept later ones
  dialog=None    leave dialogs alone (only for interactive use)
The dialogs that were seen are available afterwards in last_dialogs.

Usage:  python lib/ai_run.py <script.jsx> [--dialog enter|esc]   or   python lib/ai_run.py -e "app.version"
Module: from ai_run import run_js; run_js(code, dialog="esc", timeout=120)
"""
import sys
import threading
import time
from pathlib import Path

import pythoncom
import win32com.client

sys.path.insert(0, str(Path(__file__).parent))
import ai_dialogs  # noqa: E402

_tls = threading.local()  # COM objects cannot cross threads: one connection per thread
last_dialogs = []


class AIError(RuntimeError):
    pass


def _app():
    if getattr(_tls, "ai", None) is None:
        pythoncom.CoInitialize()
        _tls.ai = win32com.client.dynamic.Dispatch("Illustrator.Application")
    return _tls.ai


def _invoke(code):
    deadline = time.time() + 180                         # Illustrator may still be starting up
    while True:
        try:
            ole = _app()._oleobj_
            dispid = ole.GetIDsOfNames("DoJavaScript")
            break
        except pythoncom.com_error:
            _tls.ai = None
            if time.time() > deadline:
                raise
            time.sleep(3)
    r = ole.Invoke(dispid, 0, pythoncom.DISPATCH_METHOD, True, code)
    return "" if r is None else str(r)


def run_js(code: str, dialog="esc", timeout=300) -> str:
    """Run ExtendScript; the value of the last expression is returned as a string."""
    global last_dialogs
    last_dialogs = []
    box = {}

    def work():
        try:
            box["r"] = _invoke(code)
        except Exception as e:  # noqa: BLE001
            box["e"] = e
        finally:
            _tls.ai = None

    t = threading.Thread(target=work, daemon=True)
    t.start()
    t0 = time.time()
    while t.is_alive():
        t.join(0.25)
        if not t.is_alive():
            break
        if dialog:
            for h, _, title in ai_dialogs.dialogs():
                if time.time() - t0 < 0.5:
                    continue
                last_dialogs.append(title)
                if isinstance(dialog, (list, tuple)) and dialog and isinstance(dialog[0], (list, tuple)):   # one plan per dialog, in order
                    time.sleep(0.6)
                    ai_dialogs.steps(h, list(dialog[0]))
                    dialog = list(dialog[1:]) or "enter"
                elif isinstance(dialog, (list, tuple)):         # a plan for the first dialog, then accept the rest
                    time.sleep(0.6)
                    ai_dialogs.steps(h, list(dialog))
                    dialog = "enter"
                else:
                    ai_dialogs.press(h, dialog)
                time.sleep(0.4)
        if time.time() - t0 > timeout:
            ai_dialogs.answer_all("esc", 3)
            t.join(10)
            if t.is_alive():
                raise AIError(f"timeout after {timeout}s (dialogs seen: {last_dialogs})")
    if "e" in box:
        e = box["e"]
        msg = str(e)
        try:
            msg = e.excepinfo[2] or msg
        except Exception:  # noqa: BLE001
            pass
        raise AIError(msg)
    return box["r"]


RPC_E_SERVERFAULT = -2147417851


def is_fault(e):
    """Illustrator's script engine sometimes gets stuck returning RPC_E_SERVERFAULT for every call until it restarts."""
    return "-2147417851" in str(e) or "伺服器丟出一個例外" in str(e) or "server threw an exception" in str(e).lower()


def healthy():
    """True when scripts run AND menu commands work. After some failures Illustrator keeps answering simple scripts but
    every executeMenuCommand throws PARM until it restarts, so both are probed."""
    try:
        if run_js("1+1", timeout=60) != "2":
            return False
        return run_js("if (!app.documents.length) app.documents.add(); app.executeMenuCommand('deselectall'); "
                      "var t = app.activeDocument.textFrames.pointText([10, 10]); t.contents = 'x'; t.textRange.characterAttributes.size = 13; "
                      "var ok = t.textRange.characterAttributes.size == 13; t.remove(); ok ? 'ok' : 'bad'", timeout=60) == "ok"
    except Exception:  # noqa: BLE001
        return False


def restart(wait=240):
    """Kill and relaunch Illustrator (unsaved documents are lost: only use in sandbox runs)."""
    import subprocess
    subprocess.run(["taskkill", "/IM", "Illustrator.exe", "/F"], capture_output=True)
    time.sleep(6)
    _tls.ai = None
    t0 = time.time()
    while time.time() - t0 < wait:
        try:
            if run_js("app.version", timeout=wait):
                time.sleep(3)
                ai_dialogs.answer_all("esc", 2)       # recovery / crash-report prompts
                return True
        except Exception:  # noqa: BLE001
            time.sleep(3)
    return False


def run_file(path, **kw):
    return run_js(Path(path).read_text(encoding="utf-8-sig"), **kw)


if __name__ == "__main__":
    dlg = "esc"
    if "--dialog" in sys.argv:
        i = sys.argv.index("--dialog")
        dlg = sys.argv[i + 1]
        del sys.argv[i:i + 2]
    pre = ""
    if "--lib" in sys.argv:                               # prepend json.jsx + ailib.jsx (+ AI.FXDB)
        sys.argv.remove("--lib")
        from ailib_loader import library
        pre = library()
        sb = Path(__file__).resolve().parent.parent / "tests" / "sandbox.jsx"
        if sb.exists():
            pre += sb.read_text(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    if sys.argv[1] == "-e":
        print(run_js(pre + sys.argv[2], dialog=dlg))
    else:
        print(run_js(pre + Path(sys.argv[1]).read_text(encoding="utf-8-sig"), dialog=dlg))
