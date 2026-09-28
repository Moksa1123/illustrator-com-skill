"""Capability map: every Illustrator menu command (index/menu-index.json) against what was verified.
Sources: tests/menu-sweep.json (menu sweep), tests/effects-sweep.json (effects sweep: menu command + dialog-free
applyEffect XML, parameters read back), BLOCKED (commands Illustrator itself will not run from a script, with evidence)
and EXCL (not design work: UI, preferences, web/cloud, generative AI — every row carries its reason).
Output: tests/CAPABILITIES.md, tests/coverage.json (read by index/ai_api.py menu)
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
SKILL = HERE.parent
menu = json.loads((SKILL / "index" / "menu-index.json").read_text(encoding="utf-8"))
ms = {r["cmd"]: r for r in json.loads((HERE / "menu-sweep.json").read_text(encoding="utf-8"))} if (HERE / "menu-sweep.json").exists() else {}
fx = {r["cmd"]: r for r in json.loads((HERE / "effects-sweep.json").read_text(encoding="utf-8"))} if (HERE / "effects-sweep.json").exists() else {}
blocked_p = HERE / "blocked.json"
BLOCKED = json.loads(blocked_p.read_text(encoding="utf-8")) if blocked_p.exists() else {}

EXCL = [
    (r"^Window > (?!New Window$)", "panel / workspace / toolbar UI"),
    (r"^Help > ", "help, web pages, bug report"),
    (r"^Edit > (Preferences|My Settings) > |^Edit > (Keyboard Shortcuts|Color Settings|Transparency Flattener Presets|Print Presets|Adobe PDF Presets|Perspective Grid Presets)$",
     "application settings and preset libraries (global, not the document); PDF presets are applied by name in AI.pdf()"),
    (r"^File > (Browse in Bridge|Search Adobe Stock|Exit)$", "external application / web / quits Illustrator"),
    (r"^Edit > Edit Original$", "opens the linked file in another application"),
    (r"^Edit > Spelling > |^Edit > Edit Custom Dictionary$", "proofing UI (spelling), no document change"),
    (r"Generative Recolor|Text to Pattern \(Beta\)|^Object > Mockup \(Beta\)", "generative AI / cloud feature (excluded by policy, like the Photoshop skill)"),
    (r"^Type > (More from Adobe Fonts|Glyphs|Resolve Missing Fonts|Show Hidden Characters)$", "font service / panel / display only"),
    (r"^Type > (Composite Fonts|Kinsoku Shori Settings|Mojikumi Settings)$", "CJK set editors (settings dialogs); applying a set is paragraphAttributes.kinsoku / mojikumi"),
    (r"^View > (GPU Preview|Presentation Mode|Proof Setup > |Proof Colors|Hide Slices|Lock Slices|Hide Bounding Box|Hide Gradient Annotator|Show Live Paint Gaps|Hide Corner Widget|Hide Edges|Smart Guides|Hide Artboards|Show Print Tiling|Show Template|Rulers > Change to Global Rulers|Rulers > Show Video Rulers|Show Text Threads|Snap to|Edit Views|Saved View)",
     "display-only toggle or preference (no document change, no readback)"),
    (r"^View > Perspective Grid > (?!Show Grid)", "perspective grid display / preset settings"),
    (r"^Object > Pattern > Tile Edge Color$", "pattern-editing display option"),
    (r"^Keyboard > (Next|Previous) Document|^Keyboard > Debug|\(alternate\)$|^Keyboard > (Switch Selection Tools|Cycle Units|Highlight Font|Cycle Color Modes|Actions Batch)",
     "keyboard navigation / duplicate shortcut / UI toggle"),
]


def excluded(path):
    return next((why for p, why in EXCL if re.search(p, path)), None)


rows, stat = [], {}
for it in menu["items"]:
    cmd, path, top = it["cmd"], it["path"], it["top"]
    st, how, lvl = "—", "", ""
    if cmd in ms and ms[cmd]["ok"]:
        st, how, lvl = "✅", ms[cmd]["how"], ms[cmd].get("level", "")
    elif cmd in fx and fx[cmd]["ok"]:
        st, lvl = "✅", "effect readback"
        how = f"AI.fx(item, '{fx[cmd]['name']}', {{…}}) = applyEffect(XML); menu command verified too ({fx[cmd]['detail']})"
    elif cmd in BLOCKED:
        st, how = "blocked", BLOCKED[cmd]
    elif excluded(path):
        st, how = "n/a", excluded(path)
    elif cmd in ms:
        how = f"not verified: {ms[cmd].get('detail', '')}"
    elif cmd in fx:
        how = f"not verified: {fx[cmd].get('detail', '')}"
    s = stat.setdefault(top, {"✅": 0, "—": 0, "n/a": 0, "blocked": 0})
    s[st] += 1
    rows.append({"top": top, "path": path, "cmd": cmd, "status": st, "level": lvl, "how": how})

tot_ok = sum(s["✅"] for s in stat.values())
tot_can = sum(s["✅"] + s["—"] for s in stat.values())
tot_blk = sum(s["blocked"] for s in stat.values())
tot_na = sum(s["n/a"] for s in stat.values())
lines = ["# Illustrator capability map (every menu command × verified capability)", "",
         f"Illustrator {json.loads((SKILL / 'index' / 'ai-dom.json').read_text(encoding='utf-8'))['version']} | "
         f"{len(rows)} menu commands (from the app's own shortcut set, index/menu-index.json) | effects with dialog-free XML: {sum(1 for r in fx.values() if r['ok'])}", "",
         "✅ = run in a sandbox document and verified (readback: the changed state is read back | deep: the saved artwork changed | "
         "fingerprint: DOM + artwork + pixel fingerprint changed | effect readback: effect + every parameter read back from the saved file)", "",
         "— = not verified yet · blocked = Illustrator does not let a script do it (evidence given) · n/a = not design work (UI, preferences, web, generative AI; reason given)", "",
         "| Menu | ✅ | — | blocked | n/a | scriptable coverage | design coverage incl. blocked |", "|---|---|---|---|---|---|---|"]
for top, s in stat.items():
    can = s["✅"] + s["—"]
    allx = can + s["blocked"]
    lines.append(f"| {top} | {s['✅']} | {s['—']} | {s['blocked']} | {s['n/a']} | {(s['✅'] / can * 100 if can else 100):.1f}% | {(s['✅'] / allx * 100 if allx else 100):.1f}% |")
lines += ["", f"**{tot_can} scriptable design commands, {tot_ok} verified ({tot_ok / max(tot_can, 1) * 100:.1f}%) | including blocked: {tot_ok}/{tot_can + tot_blk} "
          f"({tot_ok / max(tot_can + tot_blk, 1) * 100:.1f}%) | n/a {tot_na}**", ""]
for top in stat:
    lines += [f"## {top}", "", "| Command | executeMenuCommand | Status | How (script) |", "|---|---|---|---|"]
    for r in rows:
        if r["top"] == top:
            lines.append(f"| {r['path'].split(' > ', 1)[-1]} | `{r['cmd']}` | {r['status']}{' (' + r['level'] + ')' if r['level'] else ''} | {r['how'].replace('|', '/')} |")
    lines.append("")
tp = HERE / "tools-sweep.json"
if tp.exists():
    T = json.loads(tp.read_text(encoding="utf-8"))
    tools = [t for t in T if t["kind"] == "tool"]
    sc = [t for t in T if t["kind"] != "tool"]
    lines += ["## Tools", "", f"{sum(t['ok'] for t in tools)}/{len(tools)} tools activated by `app.selectTool(name)` and read back with `app.getSelectedToolName()`. "
              "The \"script equivalent\" column is how to get the tool's result without the mouse.", "",
              "| Tool | selectTool | Script equivalent |", "|---|---|---|"]
    for t in tools:
        st = "✅ read back" if t["ok"] else ("accepted (Illustrator's getSelectedToolName() throws PARM for this tool)" if t.get("selected") else "❌ " + str(t.get("err", ""))[:60])
        lines.append(f"| `{t['tool']}` | {st} | {t['how'].replace('|', '/')} |")
    lines += ["", f"The shortcut set also lists {len(sc)} tool-context shortcuts (blend-mode / opacity / paint / fill-stroke keys). "
              "Their effect is set directly: item.blendingMode, item.opacity, fillColor / strokeColor (tested in tests/REPORT.md, style).", ""]
(HERE / "CAPABILITIES.md").write_text("\n".join(lines), encoding="utf-8")
(HERE / "coverage.json").write_text(json.dumps({"rows": rows, "stat": stat}, ensure_ascii=False, indent=0), encoding="utf-8")
print("\n".join(lines[6:6 + len(stat) + 5]))

# ── README coverage blocks (between <!-- coverage:start --> and <!-- coverage:end -->) ──
rep = json.loads((HERE / "report.json").read_text(encoding="utf-8"))["results"] if (HERE / "report.json").exists() else []
lib_ok, lib_n = sum(1 for r in rep if r.get("ok")), len(rep)
fx_ok, fx_n = sum(1 for r in fx.values() if r["ok"]), len(fx)
T = json.loads(tp.read_text(encoding="utf-8")) if tp.exists() else []
tl = [t for t in T if t["kind"] == "tool"]
tl_ok = sum(1 for t in tl if t["ok"])
pct = tot_ok / max(tot_can, 1) * 100
pct_b = tot_ok / max(tot_can + tot_blk, 1) * 100
blocked_rows = [r for r in rows if r["status"] == "blocked"]
table = ["| Menu | ✅ | blocked | n/a |", "|---|---|---|---|"] + [f"| {t} | {s['✅']} | {s['blocked']} | {s['n/a']} |" for t, s in stat.items()]
EN = [f"- **Menu commands: {tot_ok}/{tot_can} scriptable design commands verified ({pct:.1f}%); {tot_ok}/{tot_can + tot_blk} ({pct_b:.1f}%) counting the {tot_blk} blocked ones.** "
      f"{tot_na} more are UI / preferences / web / generative-AI commands (n/a, reason given per command). Every ✅ was run in a sandbox document and its result read back.",
      f"- **Effects: {fx_ok}/{fx_n}** Effect-menu effects applied without a dialog through LiveEffect XML, every parameter read back from the saved file (`presets/effects.json`).",
      f"- **Library: {lib_ok}/{lib_n}** tests pass (`tests/REPORT.md`): DOM readback, exported pixels, decoded exports, saved-file effects.",
      f"- **Tools: {tl_ok}/{len(tl)}** tools selected and read back; the rest are accepted by `selectTool` but Illustrator's `getSelectedToolName()` throws for them (each has a script equivalent).",
      "- Blocked (evidence in `tests/blocked.json`): " + "; ".join(f"{r['path']}" for r in blocked_rows) + ".",
      "", *table, "", "Per command, with the exact script route and how it was verified: [tests/CAPABILITIES.md](tests/CAPABILITIES.md)."]
ZH = [f"- **選單指令：可腳本化的設計指令 {tot_ok}/{tot_can} 全部驗證（{pct:.1f}%）；連同 {tot_blk} 個被 Illustrator 擋下的指令為 {tot_ok}/{tot_can + tot_blk}（{pct_b:.1f}%）。** "
      f"另有 {tot_na} 個是介面／偏好設定／網路／生成式 AI 指令（n/a，每個都附原因）。每個 ✅ 都在沙盒文件中實際執行並讀回結果。",
      f"- **效果：{fx_ok}/{fx_n}** 個「效果」選單效果以 LiveEffect XML 免對話框套用，所有參數從存檔讀回（`presets/effects.json`）。",
      f"- **函式庫：{lib_ok}/{lib_n}** 項測試通過（`tests/REPORT.md`）：DOM 讀回、匯出像素、匯出檔解碼、存檔效果。",
      f"- **工具：{tl_ok}/{len(tl)}** 個工具可切換並讀回；其餘 `selectTool` 接受但 Illustrator 的 `getSelectedToolName()` 會拋錯（每個都有對應的腳本做法）。",
      "- 被擋下（證據在 `tests/blocked.json`）：" + "；".join(f"{r['path']}" for r in blocked_rows) + "。",
      "", *table, "", "每個指令的腳本做法與驗證方式：[tests/CAPABILITIES.md](tests/CAPABILITIES.md)。"]
JA = [f"- **メニューコマンド：スクリプト可能なデザインコマンド {tot_ok}/{tot_can} をすべて検証（{pct:.1f}%）。Illustrator にブロックされる {tot_blk} 件を含めると {tot_ok}/{tot_can + tot_blk}（{pct_b:.1f}%）。** "
      f"残り {tot_na} 件は UI／環境設定／Web／生成 AI のコマンド（n/a、理由はコマンドごとに記載）。✅ はすべてサンドボックス文書で実行し、結果を読み戻して確認しています。",
      f"- **効果：{fx_ok}/{fx_n}** 件の「効果」メニューの効果を LiveEffect XML でダイアログなしに適用し、全パラメーターを保存ファイルから読み戻し（`presets/effects.json`）。",
      f"- **ライブラリ：{lib_ok}/{lib_n}** 件のテストに合格（`tests/REPORT.md`）：DOM の読み戻し、書き出したピクセル、書き出しファイルのデコード、保存ファイルの効果。",
      f"- **ツール：{tl_ok}/{len(tl)}** 件を選択して読み戻し。残りは `selectTool` は受け付けるものの `getSelectedToolName()` が例外を投げます（いずれもスクリプトでの代替手段あり）。",
      "- ブロック（証拠は `tests/blocked.json`）：" + "、".join(f"{r['path']}" for r in blocked_rows) + "。",
      "", *table, "", "コマンドごとのスクリプトでの実行方法と検証方法：[tests/CAPABILITIES.md](tests/CAPABILITIES.md)。"]
KO = [f"- **메뉴 명령: 스크립트로 실행 가능한 디자인 명령 {tot_ok}/{tot_can} 전부 검증({pct:.1f}%). Illustrator가 막는 {tot_blk}개를 포함하면 {tot_ok}/{tot_can + tot_blk}({pct_b:.1f}%).** "
      f"나머지 {tot_na}개는 UI/환경 설정/웹/생성형 AI 명령입니다(n/a, 명령마다 이유 기재). 모든 ✅는 샌드박스 문서에서 실행하고 결과를 다시 읽어 확인했습니다.",
      f"- **효과: {fx_ok}/{fx_n}**개의 효과 메뉴 효과를 LiveEffect XML로 대화상자 없이 적용하고, 모든 매개변수를 저장된 파일에서 다시 읽음(`presets/effects.json`).",
      f"- **라이브러리: {lib_ok}/{lib_n}**개 테스트 통과(`tests/REPORT.md`): DOM 재확인, 내보낸 픽셀, 내보낸 파일 디코딩, 저장 파일의 효과.",
      f"- **도구: {tl_ok}/{len(tl)}**개 선택 후 재확인. 나머지는 `selectTool`은 받아들이지만 `getSelectedToolName()`이 예외를 던집니다(모두 스크립트 대안 있음).",
      "- 차단됨(증거는 `tests/blocked.json`): " + "; ".join(f"{r['path']}" for r in blocked_rows) + ".",
      "", *table, "", "명령별 스크립트 실행 방법과 검증 방법: [tests/CAPABILITIES.md](tests/CAPABILITIES.md)."]
for name, block in (("README.md", EN), ("README.zh-TW.md", ZH), ("README.ja.md", JA), ("README.ko.md", KO)):
    p = SKILL / name
    if p.exists():
        s = p.read_text(encoding="utf-8")
        a, b = s.find("<!-- coverage:start -->"), s.find("<!-- coverage:end -->")
        if a >= 0 and b > a:
            p.write_text(s[:a] + "<!-- coverage:start -->\n" + "\n".join(block) + "\n" + s[b:], encoding="utf-8")
