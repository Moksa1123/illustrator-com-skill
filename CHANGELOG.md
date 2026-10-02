# Changelog

## 1.0.4 — 2026-10-02

- Size presets (54): new `momo_ad` (momo ad image, required when listing: 1000×1000, 50–1000 KB, no text / logo / frame / watermark / borders). momo main and description notes updated from the 2026-10-02 rule pages (plain background, 1–6 images, no borders, no Chinese file names; up to 20 description images); Google Ads PMax notes say not to overlay a logo and to keep one image per ratio without text.

## 1.0.3 — 2026-09-29

- `sync` on a linked checkout (`init --link`) records the checkout's version, so `info` / `check` no longer report the version from the first install and a stale "update available".

## 1.0.2 — 2026-09-29

- `tools/md_docx.py`: the PDF export works when called with a relative path or a non-ASCII (CJK) path — Word used to resolve relative paths against `C:\Windows\system32` and the export failed silently. Paths are now absolute, the PowerShell command is passed with `-EncodedCommand`, and a missing PDF raises an error.

## 1.0.1 — 2026-09-28

- `versions` / `check` / `update` no longer end with a libuv assertion on Windows (registry request through `node:https`, no forced `process.exit`).
- No DEP0190 warning when `update` runs npm / npx; the version read from the registry is validated before use.
- `compact` layouts: logo packages ship height-sized PNGs (24h–240h) and every print set (`png_sizes` in the brand config).

## 1.0.0 — 2026-09-28

First npm release.

- `illustrator-com` CLI (Node 18+, no dependencies): `init` for 14 AI assistants (Claude Code, Cursor, Windsurf,
  Antigravity, GitHub Copilot, Kiro, Codex CLI, Qoder, Cline, Gemini CLI, Trae, OpenCode, Continue, CodeBuddy),
  project or global scope; `setup`, `doctor [--smoke]`, `list`, `info`, `versions`, `update`, `check`, `config`,
  `sync`, `uninstall`.
- One shared runtime in `~/.illustrator-com-skill/`: the API index built from your Illustrator is kept across updates;
  runtime files you edited are backed up before an update replaces them.
- Update check once per session (cached 24 h), opt-in auto-update (`config auto-update on`).
- Coverage: 452/452 scriptable menu commands (99.6 % counting 2 blocked), 115/115 effects, 40/40 library tests.
- Tools: logo delivery package (`logo_package.py`), clean brand-asset folder (`brand_assets.py`), TIPO trademark form
  filler (`tipo_form.py`), Markdown → formal DOCX/PDF (`md_docx.py`).
- README in English, 繁體中文, 日本語, 한국어.
