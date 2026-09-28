# illustrator-com-skill

**English** · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

Let a coding agent (Claude Code and others) drive **Adobe Illustrator on Windows**. Every capability is checked by
running it in a sandbox document and **reading the result back** — DOM values, exported pixels, and the effect
parameters Illustrator actually stored in the saved file — never by assuming.

Companion to [photoshop-com-skill](https://github.com/Moksa1123/photoshop-com-skill), same principles.

## What's inside

| Part | What it does |
|---|---|
| `lib/ai_run.py` | Runs ExtendScript over COM and returns the result. Works when Illustrator's COM type library is unregistered (`TYPE_E_LIBNOTREGISTERED`), never shows the "run this script?" prompt, and **answers Illustrator's modal dialogs itself**: cancel (default, so nothing hangs), accept, or fill fields in (`["sel", "type:30", "tab", "ok"]`). Detects and recovers a faulted script engine. |
| `lib/ailib.jsx` | A tested design library with top-left artboard coordinates: shapes and SVG path data, RGB / CMYK / spot / gradient color, stroke styles, mixed-style text, text on a path, fit text, character/paragraph styles, find & replace keeping styles, Pathfinder (unite, minus front, intersect, exclude, divide, trim, merge, crop, outline), align / distribute / grid, clipping, compound paths, symbols, graphic styles, repeat, blends, place / embed / Image Trace / rasterize, recolor, new documents with safe-zone guides, and PNG / JPG / WebP / SVG / PDF / PSD / Export for Screens. |
| `presets/effects.json` | **Every Effect-menu effect as dialog-free `applyEffect` XML** (drop shadow, glows, warps, 3D and Materials, Photoshop filters …) with default parameters and types, all read back from Illustrator's own saved files. |
| `lib/fingerprint.jsx`, `tools/ai_dump.py` | Document fingerprint (every DOM part) plus a reader for uncompressed `.ai` files that recovers what the DOM hides: live effects with every parameter (including the binary Photoshop-filter descriptors) and a stable art hash. |
| `index/` | API index **built from your own Illustrator** (type library inside `ScriptingSupport.aip` + runtime reflection), the full menu-command list captured from the app's Keyboard Shortcuts set, and a query tool (`find`, `class`, `enum`, `member`, `menu`, `effect`, `stats`). |
| `tests/` | Library tests (`run_tests.py` → `REPORT.md`) and sweeps of every menu command, effect and tool (`menu_sweep.py`, `effects_sweep.py`, `tools_sweep.py`) → `CAPABILITIES.md`: how to do each one from a script and how it was verified. |
| `presets/sizes.json` + `tools/sizes.py` | 53 design-size presets (Instagram, Facebook, Open Graph, LINE, YouTube, TikTok, Google Ads, Amazon, Shopify, Etsy, Shopee, momo…) with safe zones and sources; `new <id>` opens the artboard with guides. |
| `tools/html2ai.py` | Fixed-size HTML layout → **editable vector** Illustrator document: boxes become shapes (fill, linear gradient, border, radius, shadow), photos are embedded as displayed, inline SVG is imported as paths, text becomes real text frames. |
| `tools/logo_package.py`, `tools/brand_assets.py` | Industry-standard **logo delivery package** from a finished logo kit (one JSON config): RGB vectors; print-ready CMYK AI / EPS / PDF-X-1a with greys forced to K-only, brand ink K values and spot-colour plates, audited per file; PNG 64–4096 px at 300 ppi; social avatars / covers / Open Graph / e-mail; favicon + app icons; then re-filed into a clean use-first folder (Print / Digital / Social / Web / Card / Guidelines / Source / Trademark). |
| `tools/tipo_form.py`, `tools/md_docx.py` | Trademark filing helpers for Taiwan (TIPO): trademark drawings (JPG + TIF, 300 dpi, 7.6 cm), the official T0101 application form filled in (check boxes ticked in the form's own bordered boxes), and Markdown → formal DOCX/PDF via Word (repeating table headers, rows never split). |
| `tools/ui.py`, `tools/capture_commands.py`, `tools/make_graph_fixture.py` | Screen/keyboard control limited to Illustrator windows, for the few things that only exist on screen. |

## Verified coverage (Illustrator 2024 / 28.0)

<!-- coverage:start -->
- **Menu commands: 452/452 scriptable design commands verified (100.0%); 452/454 (99.6%) counting the 2 blocked ones.** 181 more are UI / preferences / web / generative-AI commands (n/a, reason given per command). Every ✅ was run in a sandbox document and its result read back.
- **Effects: 115/115** Effect-menu effects applied without a dialog through LiveEffect XML, every parameter read back from the saved file (`presets/effects.json`).
- **Library: 40/40** tests pass (`tests/REPORT.md`): DOM readback, exported pixels, decoded exports, saved-file effects.
- **Tools: 60/85** tools selected and read back; the rest are accepted by `selectTool` but Illustrator's `getSelectedToolName()` throws for them (each has a script equivalent).
- Blocked (evidence in `tests/blocked.json`): File > Save Selected Slices; File > Print.

| Menu | ✅ | blocked | n/a |
|---|---|---|---|
| File | 21 | 2 | 3 |
| Edit | 25 | 0 | 29 |
| Object | 124 | 0 | 5 |
| Type | 48 | 0 | 7 |
| Select | 39 | 0 | 0 |
| Effect | 119 | 0 | 0 |
| View | 40 | 0 | 45 |
| Window | 1 | 0 | 63 |
| Help | 0 | 0 | 7 |
| Keyboard | 35 | 0 | 22 |

Per command, with the exact script route and how it was verified: [tests/CAPABILITIES.md](tests/CAPABILITIES.md).
<!-- coverage:end -->

## Install

Needs Windows 10/11, Adobe Illustrator, Python 3.9+ and Node 18+.

```bash
npm install -g illustrator-com-skill
illustrator-com init --ai claude -g      # or: npx illustrator-com-skill init --ai claude -g
illustrator-com setup                    # pip install -r requirements.txt + API index from your Illustrator + doctor
```

`init` copies the runtime (`lib/`, `tools/`, `index/`, `tests/`, `presets/`) to `~/.illustrator-com-skill/` once and
writes a `SKILL.md` for each assistant that points at it, so the API index built from your Illustrator is shared by every
assistant and survives updates.

```bash
illustrator-com init                     # pick assistants interactively
illustrator-com init --ai cursor,windsurf  # this project only (.cursor/skills/…, .windsurf/skills/…)
illustrator-com init --ai all -g         # every assistant that has a user-wide skills folder
illustrator-com doctor --smoke           # Windows, Python, packages, Illustrator COM, index, one real script
illustrator-com list | info | versions | uninstall [--purge]
```

### 14 AI platforms

| `--ai` | Assistant | Project | Global (`-g`) |
|---|---|---|---|
| `claude` | Claude Code | `.claude/skills/illustrator-com/` | `~/.claude/skills/` |
| `cursor` | Cursor | `.cursor/skills/illustrator-com/` | `~/.cursor/skills/` |
| `windsurf` | Windsurf / Devin Desktop | `.windsurf/skills/illustrator-com/` | — |
| `antigravity` | Antigravity / generic agent | `.agent/skills/illustrator-com/` | `~/.gemini/antigravity/global_skills/` |
| `copilot` | GitHub Copilot | `.github/skills/illustrator-com/` | `~/.copilot/skills/` |
| `kiro` | Kiro | `.kiro/skills/illustrator-com/` | — |
| `codex` | Codex CLI | `.codex/skills/illustrator-com/` | `~/.codex/skills/` |
| `qoder` | Qoder | `.qoder/skills/illustrator-com/` | — |
| `cline` | Cline | `.cline/skills/illustrator-com/` | `~/.cline/skills/` |
| `gemini` | Gemini CLI | `.gemini/skills/illustrator-com/` | `~/.gemini/skills/` |
| `trae` | Trae | `.trae/skills/illustrator-com/` | — |
| `opencode` | OpenCode | `.opencode/skills/illustrator-com/` | — |
| `continue` | Continue | `.continue/skills/illustrator-com/` | — |
| `codebuddy` | CodeBuddy | `.codebuddy/skills/illustrator-com/` | — |

The assistant has to run on the Windows machine that has Illustrator: cloud agents (Claude.ai web, Copilot coding
agent, Codex cloud) cannot reach a local Illustrator.

### Updates

```bash
illustrator-com update                   # latest npm version -> runtime + every recorded install
illustrator-com check                    # is there a newer version? (cached for 24 h)
illustrator-com config auto-update on    # let `check` install updates by itself
```

Every installed `SKILL.md` asks the agent to run `check --quiet` once per session, so you hear about a new version
without doing anything. Auto-update is **off** by default: an update never lands in the middle of your work unless you
turn it on. Updates keep your API index (`index/ai-dom.json`) and back up any runtime file you edited
(`~/.illustrator-com-skill/_state/backup/`).

Working on the skill itself: `node bin/illustrator-com.mjs init --link --ai claude -g` points the runtime at your
checkout instead of copying it.

## Quick start

```bash
python lib/ai_run.py -e "app.version"
python tests/run_tests.py                  # what works on your Illustrator -> tests/REPORT.md
python index/build_index.py                # API index from your Illustrator
python index/ai_api.py find gradient stop
python index/ai_api.py menu pathfinder     # menu commands + their verified status
python index/ai_api.py effect shadow       # dialog-free effect XML
python tools/sizes.py new ig_story_reel    # 1080x1920 artboard with safe-zone guides
python tools/html2ai.py tests/fixtures/fixture.html out/card.ai --w 600 --h 800 --png out/card.png
```

```python
import sys; sys.path.insert(0, "lib")
from ai_run import run_js
from ailib_loader import library
run_js(library() + """
AI.newDoc(1080, 1080, 'post', {bg: '#f4f2ee', safe: [60, 60, 60, 60]});
var card = AI.roundRect(90, 90, 900, 900, 40, {fill: AI.gradient([[0, '#c8a97e'], [1, '#8c6f52']], {angle: 90}), stroke: null});
AI.dropShadow(card, {y: 10, blur: 14, opacity: 0.3});
AI.text('Bean & Heart', 140, 160, {font: 'Georgia-Italic', size: 110, color: '#2b2520'});
var badge = AI.pathfinder([AI.circle(880, 880, 90), AI.star(880, 880, 60, 25, 5)], 'minusFront');
AI.style(badge, {fill: '#2b2520', stroke: null});
AI.png('C:/out/post.png'); AI.svg('C:/out/post.svg', {outlineText: true}); 'ok'
""")
```

## Principles

- **Verify, don't assume.** "No error" is not proof: a menu command issued in the same call that made the selection
  silently acts on the old one, many DOM writes are ignored without an error, and a dialog left open blocks everything. Every row in `CAPABILITIES.md` was run and read back.
- **Dialogs are part of the API.** Commands that only have a dialog are driven through the dialog (fields typed,
  OK clicked), and only Illustrator's dialog window ever receives keystrokes.
- **No generative AI features** (Generative Recolor, Text to Pattern, Mockup beta) — same policy as the Photoshop skill.
- **Sizes change.** Every preset carries its source and a checked date. Re-check before a big campaign.

## Requirements

Windows 10/11, Python 3.9+, Node 18+ (installer only). Developed and verified on Illustrator 2024 (28.0); other versions should work through the same COM interface but are untested, so run `tests/run_tests.py` and the sweeps on yours. macOS would need an AppleScript
`do javascript` bridge.

Troubleshooting: `docs/troubleshooting-com.md` · Sizes: `docs/sizes.md`

## License

MIT, see `LICENSE` and `NOTICE`. No Adobe documentation or third-party index is redistributed; the API index is generated
locally from your own Illustrator installation.
