# Troubleshooting Illustrator COM on Windows

## Symptom: `TYPE_E_LIBNOTREGISTERED` (0x8002801D) / 「程式庫未登錄」

Illustrator starts, but COM calls fail from PowerShell (`New-Object -ComObject Illustrator.Application`), win32com
early binding, and most bridges.

```powershell
$clsid = (Get-ItemProperty 'Registry::HKEY_CLASSES_ROOT\Illustrator.Application\CLSID').'(default)'
(Get-ItemProperty "Registry::HKEY_CLASSES_ROOT\CLSID\$clsid\LocalServer32").'(default)'   # ...\Illustrator.exe /Automation
$tl = (Get-ItemProperty "Registry::HKEY_CLASSES_ROOT\CLSID\$clsid\TypeLib").'(default)'
Test-Path "Registry::HKEY_CLASSES_ROOT\TypeLib\$tl"                                        # False = the problem
```

`lib/ai_run.py` never uses the type library: it calls `IDispatch::GetIDsOfNames("DoJavaScript")` and `Invoke`.
The type library itself is still readable from `Plug-ins/Extensions/ScriptingSupport.aip` (`index/build_index.py`
loads it with `pythoncom.LoadTypeLib`). To fix registration for other tools: Creative Cloud → Illustrator → Repair.

## Symptom: the first call fails with E_FAIL (0x80004005) for ~20 s

Illustrator is still starting (COM launched it). `run_js` retries `GetIDsOfNames` for up to 3 minutes.

## Symptom: every call returns RPC_E_SERVERFAULT (0x80010105, 「伺服器丟出一個例外」)

Illustrator's script engine is stuck (seen after heavy 3D / Photoshop-filter effects, or after a script touched an
unsafe property getter). The UI still works, but no script runs until Illustrator restarts.
`ai_run.healthy()` detects it; `ai_run.restart()` kills and relaunches Illustrator (unsaved work is lost — the sweeps
only use sandbox documents).

## Symptom: a script never returns

A modal dialog is open (many menu commands have one). `run_js(..., dialog="esc")` (the default) cancels dialogs;
`dialog="enter"` accepts them; a list plan fills them in. Dialogs are found as Illustrator-owned `#32770` or
`StandardMultiplugin_WindowClass` windows, or any Illustrator window while the main window is disabled; real OK /
Cancel buttons are clicked with `BM_CLICK`, other dialogs get keystrokes only while they are the foreground window.

## Symptom: "You are about to run a script…" dialog

Only when a `.jsx` is opened with `Illustrator.exe script.jsx` or File > Scripts. `run_js` never triggers it.
