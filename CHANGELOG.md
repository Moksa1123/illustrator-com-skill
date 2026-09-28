# Changelog

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
