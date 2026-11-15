---
name: illustrator-com
user-invocable: true
description: Drive Adobe Illustrator on Windows from an agent. Runs ExtendScript over COM with no "run script?" dialog, even when the COM type library is unregistered, and answers Illustrator's modal dialogs by itself (accept, cancel, or fill in fields) so menu commands that only have a dialog still run. Looks up the real API from an index built from your own Illustrator (158 classes; every member checked at runtime and marked verified, COM-only or unverified), runs every menu command by its executeMenuCommand name (635 commands captured from the app itself, per-command capability map), applies any of 115 live effects without a dialog through verified LiveEffect XML (parameters read back from the saved file), and uses a tested library for design work (top-left artboard coordinates, shapes, SVG path data, CMYK/spot/gradient colors, mixed-style text, text on path, pathfinder, align/distribute, clipping, symbols, image place/embed/trace, repeat, blends, new documents with safe-zone guides, PNG/JPG/WebP/SVG/PDF/PSD and Export for Screens). Also includes 54 design-size presets (Instagram, Facebook, LINE, YouTube, TikTok, Google Ads, Amazon, Shopee…), HTML-to-editable-vector conversion, and document fingerprints that prove a command really changed something.
---

# Illustrator over COM (Windows)

## Sources

Every lookup answers from data taken from a real Illustrator, not from Adobe's (partly wrong) scripting guide.
The counts and dates below are checked against the data by `python tools/check_numbers.py` (it fails when they drift).

| Data | Count | Taken from | Measured | Confidence |
|---|---|---|---|---|
| `index/ai-dom.json` (built locally, not shipped) | 158 classes, 2715 members: 1781 verified in ExtendScript, 684 COM-only, 250 unverified | type library in `ScriptingSupport.aip` + runtime reflection, Illustrator 28.0.0 | 2026-09-28 | measured (`?` = in the type library only) |
| `index/menu-index.json` + `tests/coverage.json` | 635 menu commands: 452 run and read back, 181 n/a (UI/settings), 2 blocked | the app's own Keyboard Shortcuts set (`.kys`) + `tests/menu_sweep.py` | 2026-09-28 | measured |
| `presets/effects.json` | 115 live effects, all applied and read back | `tests/effects_sweep.py`, parameters read from the saved `.ai` | 2026-09-28 | measured |
| `index/terms_zh.csv` | 206 zh_TW-English menu label pairs | Illustrator's zh_TW Export Text aligned to the menu index (`index/build_zh_terms.py`) | 2026-11-16 | `shortcut` exact; `between` paired by position |
| `index/glossary_zh.csv` | 67 hand-made design terms | zh labels checked against the zh_TW export | 2026-11-16 | `ui-string` / `inferred` per row |
| `presets/sizes.json` | 54 design-size presets | platform help pages (URL per preset) | 2026-10-02 | 33 official, 21 widely-cited |
| `tests/REPORT.md` | 40/40 library tests | `tests/run_tests.py` in Illustrator 28.0.0 | 2026-09-28 | measured |

Live numbers: `python index/ai_api.py stats`.

## Usage

Use for: scripting Adobe Illustrator on Windows (shapes, text, color, effects, menu commands, export), design-size
presets, HTML to editable vector, logo delivery packages, Taiwan trademark drawings.
Don't use for: Photoshop work (use `photoshop-design`); em925 brand vector work (the `em925-向量圖` session);
macOS (COM is Windows-only); generative AI features (Text to Vector, Generative Recolor: excluded).

**Entry point for every lookup: `python index/ai_api.py <find|class|enum|member|menu|effect|stats> ...`** (stdlib only,
no Illustrator needed). Everything that touches Illustrator goes through `run_js` in `lib/ai_run.py`.

Dependencies: the lookup layer (`index/ai_api.py`, `tools/sizes.py list|show`, `tools/check_numbers.py`,
`tests/test_*.py`, `evals/grade.py`) is Python stdlib only. Driving Illustrator needs `pywin32`, `psutil`, `pywinauto`
(`requirements.txt`): COM and dialog automation cannot be done with the standard library.

Tools in the table below are for you, except the maintainer-only rebuilders: `index/build_*.py`,
`tools/capture_commands.py`, `tests/*_sweep.py`, `tests/build_coverage.py`, `tools/check_numbers.py`.

| Path | What |
|---|---|
| `lib/ai_run.py` | `run_js(code, dialog=…)` calls `DoJavaScript` through raw `IDispatch` (no type library, no dialog). A watchdog answers Illustrator dialogs: `"esc"` (default, never hangs), `"enter"` (accept defaults), or a plan like `["sel", "type:30", "tab", "ok"]`. `restart()` recovers a faulted script engine. |
| `lib/ailib.jsx` + `lib/ailib_loader.py` | Tested library `AI.*` (see below). `library()` returns json.jsx + ailib.jsx + `AI.FXDB` (verified effect defaults). |
| `lib/fingerprint.jsx`, `tools/ai_dump.py` | `FP()` / `FPDIFF()` hash every part of the DOM; `ai_dump.py` reads what the DOM cannot see from an uncompressed `.ai` save: live effects with every parameter, and a stable art hash. |
| `index/build_index.py`, `index/ai_api.py` | API index from **your** Illustrator (type library in `ScriptingSupport.aip` + runtime reflection). Query: `find`, `class`, `enum`, `member`, `effect`, `menu`, `stats`. |
| `index/build_menu_index.py`, `tools/capture_commands.py` | Every menu command with its `executeMenuCommand` string, captured from the app's own Keyboard Shortcuts set. |
| `presets/effects.json` | Every Effect-menu effect as dialog-free `applyEffect` XML with default parameters and types (`tests/effects_sweep.py`). |
| `tests/run_tests.py` → `tests/REPORT.md` | Library tests; each reads the result back (DOM, exported pixels, saved-file effects, exported files decoded). |
| `tests/menu_sweep.py`, `tests/effects_sweep.py`, `tests/tools_sweep.py`, `tests/build_coverage.py` → `tests/CAPABILITIES.md` | Every menu command and tool run in a sandbox and verified; how to do each from a script. |
| `presets/sizes.json` + `tools/sizes.py` | 54 design-size presets with safe zones, file limits, sources. `list <kw>`, `show <id>`, `new <id>` (artboard + safe-zone guides). |
| `tools/html2ai.py` | Fixed-size HTML layout → editable Illustrator document: vector boxes (fill, gradient, border, radius, shadow), embedded photos, imported inline SVG, real text frames. |
| `tools/logo_package.py` | Industry-standard logo delivery package from a finished logo kit: RGB vectors; CMYK print AI / EPS / PDF-X-1a (greys forced K-only, brand ink K values, spot-colour plates) with a per-file colour audit; PNG 64–4096; social avatars / covers / Open Graph / e-mail; favicon + app icons; README with colour specs. |
| `tools/brand_assets.py` | Re-files a logo package into a clean, use-first delivery folder (Print / Digital / Social / Web / Card / Guidelines / Source / Trademark) with ASCII filenames, a README, and trademark drawings for TIPO (JPG + TIF, 300 dpi, 7.6 cm, white background, cropped to the mark). |
| `tools/tipo_form.py`, `tools/md_docx.py` | Taiwan trademark filing: fills the official TIPO T0101 form (`V` in the form's own bordered boxes, PDF via Word); Markdown → formal DOCX/PDF (repeating table headers, unsplit rows, chapter page breaks). |
| `tools/ui.py`, `tools/ui_drive.py` | Screenshot plus key/mouse input limited to Illustrator windows, for the rare thing that is only on screen. |

## Routing

**Look it up first, never answer from memory.** Every API name, `executeMenuCommand` string, LiveEffect name and
XML parameter comes out of `ai_api.py`; Adobe's scripting guide and memory are both often wrong. If a lookup finds
nothing, say so, mark it 待補 (pending) and add a row to `data/pending.csv` (date, question, why not found, asked by).
Never guess a name.

Chinese works in every lookup (`index/terms_zh.csv`, `index/glossary_zh.csv`): `menu 建立外框`, `effect 陰影`, `find 漸層`.

| The user says | Data | Command |
|---|---|---|
| set X on an object, 屬性, 方法, 物件模型 | `index/ai-dom.json` | `ai_api.py find <words>`, then `class <Class>` / `member <Class.member>` |
| an enum value, 漸變模式, PDF 標準 | `index/ai-dom.json` | `ai_api.py enum <Enum>` |
| a menu item, 選單指令, 建立外框, 外框筆畫, 擴充外觀, 剪裁遮色片 | `index/menu-index.json` + `tests/coverage.json` | `ai_api.py menu <words>` (status ✅ / n/a / blocked + the scripted "How") |
| an Effect-menu effect, 效果, 陰影, 光暈, 羽化, 模糊, 圓角 | `presets/effects.json` | `ai_api.py effect <words>` (LiveEffect name + default XML) |
| does X work on this version, 能不能做 | `tests/REPORT.md`, `tests/CAPABILITIES.md` | read the row; not there = untested |
| an IG / FB / LINE / YouTube / Shopee size, 尺寸, 安全區 | `presets/sizes.json` | `tools/sizes.py list <kw>`, `show <id>` |
| what a saved .ai really contains | the file | `tools/ai_dump.py effects file.ai` |
| how many / which version | all of the above | `ai_api.py stats` |

## Tasks

| Task | Steps | Done when |
|---|---|---|
| Social post / banner | `sizes.py show <id>`, `AI.newDoc(w, h, name, {safe})`, shapes/text with `AI.*`, `AI.png/jpg/webp` | exported file has the preset's pixel size; safe-zone guides present |
| HTML layout to editable .ai | `python tools/html2ai.py page.html out.ai` | real text frames and vector boxes; `tests/html2ai_check.py` passes after converter changes |
| Run a menu command | `ai_api.py menu <words>`; select in one `run_js` call, `app.executeMenuCommand('<cmd>')` in the next | `FPDIFF()` shows the change (not just "no error") |
| Apply a live effect | `ai_api.py effect <words>`, then `AI.fx(item, '<LiveEffect name>', {param: v})` | `ai_dump.py effects` on an uncompressed save lists it with your parameters |
| Effect with unknown parameters | apply once through the menu, save an uncompressed `.ai`, `ai_dump.py effects file.ai` | parameter names read back from the file |
| Dialog-only command | `run_js(code, dialog=["sel", "type:30", "tab", "ok"])` | readback of the value typed |
| Logo delivery package | `python tools/logo_package.py <kit.json>` (see `examples/logo_package.example.json`) | colour audit: print files have no non-K greys; all PNG sizes present |
| Trademark (TIPO) drawings + form | `tools/brand_assets.py`, then `tools/tipo_form.py` | JPG + TIF, 300 dpi, 7.6 cm, white background; form PDF opens |

### Run code
```python
import sys; sys.path.insert(0, "lib")
from ai_run import run_js
from ailib_loader import library
print(run_js(library() + """
var D = AI.newDoc(1080, 1350, 'post', {safe: [0, 45, 0, 45], bg: '#f4f2ee'});
var t = AI.text('Bean & Heart', 80, 120, {font: 'Georgia-Italic', size: 96, color: '#8c6f52'});
AI.dropShadow(AI.roundRect(80, 300, 920, 700, 32, {fill: AI.gradient([[0, '#c8a97e'], [1, '#8c6f52']], {angle: 90})}), {y: 8, blur: 12, opacity: 0.3});
AI.png('C:/out/post.png'); 'done'
"""))
```
Coordinates are artboard-relative, **top-left origin, y down, in points** (`AI.box(item)` reads them back). Colors: `[r,g,b]`, `'#hex'`, `{c,m,y,k}`, `{gray}`, `{spot, color, tint}`.

Library (all tested, see tests/REPORT.md): shapes `rect roundRect ellipse circle polygon star line path svgPath` · color `rgb cmyk gray hex spotColor swatch gradient` · `style layer` · layout `moveTo scaleTo rotate flip align distribute grid box` · structure `group ungroup clip compound repeat blend symbol placeSymbol graphicStyle` · text `text runs textAttrs textOnPath fitText outline charStyle paraStyle findText replaceText font` · effects `fx dropShadow outerGlow innerGlow feather roundCorners offsetPath gaussianBlur warp roughen expandAppearance` · `pathfinder(items, 'unite'|'minusFront'|'intersect'|'exclude'|'divide'|'trim'|'merge'|'crop'|'outline'|'minusBack')` · images `place trace rasterize recolor` · document `newDoc safeGuides addArtboard fitArtboard` · export `png jpg webp svg pdf psd saveAI exportScreens`.

### Rules
1. **Check `tests/REPORT.md` and `tests/CAPABILITIES.md` first.** Use verified functions and the "How" column.
2. **Adding a capability means adding a test that reads back** Illustrator's state (DOM value, exported pixels, or `ai_dump.py` on a saved `.ai`). "No error" is not a pass: Illustrator silently ignores many things.
3. **Don't guess names.** `python index/ai_api.py find <words>`, `class <Class>`, `enum <Enum>`; menu commands: `ai_api.py menu <words>`; effects: `ai_api.py effect <words>`.
4. Call Illustrator only through `run_js`. Never launch `Illustrator.exe script.jsx` (it prompts). Keep `dialog="esc"` unless you mean to accept or fill in a dialog.
5. End scripts with an expression; its string value is returned (`J(obj)` for JSON). A top-level `return` is a syntax error.
6. `restart()` kills Illustrator: only use it on sandbox documents. Save user work first.
7. Swatches, brushes, symbols and graphic-style **libraries** are user data: don't delete presets; tests only touch sandbox documents.

### Finding how to do something (in order)
1. `ai_api.py find …` — the DOM (most object properties are writable and readable).
2. `ai_api.py menu …` — `app.executeMenuCommand('<name>')` runs any menu command on the current selection; `tests/CAPABILITIES.md` says whether it needs a dialog and how the sweep answered it.
3. `ai_api.py effect …` — live effects: `AI.fx(item, '<LiveEffect name>', {param: value})` or `item.applyEffect(xml)`. To learn a new effect's parameters: apply it once through the menu, save an uncompressed `.ai`, `python tools/ai_dump.py effects file.ai`.
4. A dialog-only command: `run_js(code, dialog=["sel", "type:30", "tab", "ok"])` types into the dialog (only the dialog window receives keys).

### Pitfalls
- `pathItems.rectangle(top, left, w, h)` uses document coordinates (y up); `AI.rect(x, y, w, h)` uses artboard top-left coordinates. Point text is placed by its **baseline**; `AI.text` moves it so the top of the text box is at y (pass `{anchor: 'baseline'}` to keep the baseline).
- New documents from `app.documents.add()` use the last-used profile; `AI.newDoc` uses an explicit `DocumentPreset` (units, color mode, artboards, bleed).
- `executeMenuCommand` throws **PARM** both for an unknown name and for a few real ids Illustrator refuses to scripts (Type on a Path effects, Trim View, isolation mode…). `tests/CAPABILITIES.md` gives the working route for each: a DOM equivalent, or the real menu bar through `tools/menu_ui.py` (reads the native popup menus and clicks the item).
- **Illustrator refreshes command targets only when idle.** A menu command issued in the same `run_js` call that created or selected the objects often acts on the *old* selection (or silently does nothing). Select in one call, run the command in the next.
- **Object references go stale between calls**: a variable kept from an earlier `run_js` call can keep reporting old geometry. Look items up again (`pageItems.getByName`) at the start of each call; counts (`pathItems.length`) read in the creating call can be stale too.
- **After a call adds a layer, `document.pathItems.add()` / `textFrames` keep inserting into that layer for the rest of the call**, whatever `activeLayer` says (a locked one fails with 8705 "Target layer cannot be modified"). The library creates art in `document.activeLayer` explicitly (`AI.T()`); do the same in raw DOM code. `AI.safeGuides` locks the guide items, not the Guides layer.
- Stacking order matters for pathfinder (`minusFront` keeps the back shape): `AI.group` keeps the items' original stacking order; `AI.pathfinder` returns the single resulting shape (not its wrapper group) when there is one, and `AI.style` on a group paints every shape inside.
- Give Illustrator an idle moment (~0.6 s between calls) after `consolidateAllWindows`, `fitin`, or a scripted selection before a menu command: commands like Select > Inverse or Select > Object > Clipping Masks otherwise act on nothing, intermittently.
- ExtendScript is ES3: no `Array.prototype.indexOf/map/forEach`. `name` is a global (the app name) — never use it as a variable in scripts.
- PDF presets such as `[Press Quality]` reset the document bleed to 0 in the saved PDF. For print, leave `pDFPreset` unset and use `pDFXStandard = PDFXStandard.PDFX1A2001` + `trimMarks = true` (bleed kept, verified with the PDF's BleedBox). `DocumentPreset.documentBleedOffset` does set the bleed.
- `groupItems.createFromFile(svg)` / placing an SVG scales geometry but not stroke widths or dash lengths when you resize afterwards: judge line weights on the outlined result (`app.executeMenuCommand('OffsetPath v22')` = Outline Stroke, dashes become dots).
- Blend Options (spacing = specified steps) could not be set by dialog automation (UIA / WM_SETTEXT / keyboard all kept 8 steps); generate the intermediate paths yourself for line-art blends.
- Never hold two `characterAttributes` objects of the same frame at once — they alias; read values one at a time.
- Dialog fields: typing needs Tab to commit before OK; UI Automation (`uia:<n>:<value>`, `uiaclick:<label>` steps in a dialog plan) sets fields and radios without keyboard focus. Photoshop-filter effects keep their parameters in a binary descriptor (`tools/ai_dump.py` decodes it).
- Dialogs remember last-used values (e.g. Split Into Grid 1×1, Mosaic Tiles size): always set the fields you rely on.
- Right after a dialog closes Illustrator can briefly refuse `saveAs` ("No such element"): retry after a short sleep (`SAVEAI` does).
- Illustrator's script engine occasionally faults (every call returns RPC_E_SERVERFAULT) until restart; `ai_run.healthy()` / `restart()`.
- Repeat items' `radialConfig` / `gridConfig` / `symmetryConfig` getters return "NULL pointer" in 28.0; use Object > Repeat > Options (dialog plan) instead.
- Text `characters[i]` is a TextRange: set `.length` to widen it before changing attributes (`AI.runs`, `AI.replaceText` keep styles this way).

## Verify

Never report "done" on "no error": Illustrator silently ignores many things. Read the result back.

| Output | Verifier | Pass |
|---|---|---|
| any document change | `FP()` before, `FPDIFF()` after (`lib/fingerprint.jsx`) | the expected part of the DOM changed |
| live effects | `python tools/ai_dump.py effects file.ai` (uncompressed save) | the effect is listed with the parameters set |
| exported PNG/JPG/WebP | open the file, check pixel size; sample pixels as `tests/run_tests.py` does | size matches the preset; colours as specified |
| print PDF | the PDF's BleedBox / TrimBox | bleed kept (not 0) |
| logo package | the package report's `print_colour_audit` | `nonK` = 0 for every print file |
| html2ai changes | `python tests/html2ai_check.py` | exit 0 |
| library changes | `python tests/run_tests.py` (writes `tests/REPORT.md`) | all pass (last run 40/40, 2026-09-28) |
| lookup data / this file | `python -m unittest discover -s tests -p "test_*.py"` (offline, no Illustrator), `python tools/check_numbers.py` | all OK, exit 0 |

## Maintenance

```
illustrator-com setup                # pip install -r requirements.txt, API index from your Illustrator, doctor
illustrator-com doctor --smoke       # what is missing, and one real script in Illustrator
python tests/run_tests.py            # what works on your version -> tests/REPORT.md
```
Without the npm CLI: `pip install -r requirements.txt`, then `python index/build_index.py`. Re-capture the menu-command
list after an Illustrator upgrade: `python tools/capture_commands.py`, then `python index/build_menu_index.py`.

After an Illustrator upgrade: `python index/build_index.py`, `python tools/capture_commands.py`,
`python index/build_menu_index.py`, `python index/build_zh_terms.py` (needs a zh_TW Export Text in `index/raw/`),
`python tests/menu_sweep.py`, `tests/effects_sweep.py`, `tests/build_coverage.py`, `python tests/run_tests.py`,
then `python tools/check_numbers.py` and update the Sources table until it passes.

Evals: `python evals/grade.py --questions`, answer with and without the skill, then
`python evals/grade.py --with ... --without ... --write` (appends to `evals/RESULTS.md`).
After editing this file: `node bin/illustrator-com.mjs sync` (copies it to the installed skill).
