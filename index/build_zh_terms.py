"""Chinese (zh_TW) <-> English menu-command glossary, taken from YOUR Illustrator.

Edit > Keyboard Shortcuts > Export Text writes the localized menu labels in menu order
(index/raw/shortcuts_zh_TW.txt). The localized list skips some commands and has no command ids, so it is aligned to
index/menu-index.json per top-level menu with a sequence alignment; keyboard shortcuts are the anchors.

Output: index/terms_zh.csv  zh,en_path,cmd,shortcut,anchor,source
  anchor = shortcut  the shortcut matches on both sides (exact)
  anchor = between   the only line between two shortcut anchors whose count matches on both sides (by position)
Lines that cannot be placed this way are left out; index/glossary_zh.csv covers the common ones by hand.
Hand-made design terms live in index/glossary_zh.csv (not touched here).
Usage: python index/build_zh_terms.py [--review]   (--review prints every pair)
"""
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw"
TOPS = [("File", "檔案(F)"), ("Edit", "編輯(E)"), ("Object", "物件(O)"), ("Type", "文字(T)"), ("Select", "選取(S)"),
        ("Effect", "效果(C)"), ("View", "檢視(V)"), ("Window", "視窗(W)"), ("Help", "說明(H)"), ("Keyboard", "其他選項")]
SC = re.compile(r"\s*((?:(?:Alt|Shift|Ctrl)\+)*(?:F\d{1,2}|Tab|Ctrl\+\+|.))\s*$")


def split_label(line):
    """'另存新檔(A)Shift+Ctrl+S' -> ('另存新檔', 'Shift+Ctrl+S')."""
    m = re.match(r"^(.*?)((?:(?:Alt|Shift|Ctrl)\+)+(?:F\d{1,2}|Tab|.+)|\s?F\d{1,2})?$", line)
    label, sc = (m.group(1), (m.group(2) or "").strip()) if m else (line, "")
    if not label.strip():          # the whole line looked like a shortcut
        label, sc = line, ""
    label = re.sub(r"\([A-Z0-9]\)$", "", label.strip()).strip()
    return label, sc


def shortcut(key, mods):
    if not key:
        return ""
    parts = [n for bit, n in ((128, "Alt"), (32, "Shift"), (64, "Ctrl")) if mods & bit]
    k = {9: "Tab"}.get(key)
    if k is None:
        k = f"F{key - 111}" if 112 <= key <= 123 else chr(key).upper()
    return "+".join(parts + [k])


def norm_sc(s):
    s = s.replace(" ", "")
    if not s:
        return ""
    *mods, k = s.split("+") if not s.endswith("++") else s[:-2].split("+") + ["+"]
    if s.endswith("++") and mods and mods[-1] == "":
        mods = mods[:-1]
    return "+".join(sorted(m for m in mods if m) + [k.upper()])


def nodes_for(items):
    """English menu nodes in menu order: submenu headers (once) and leaf commands."""
    out, seen = [], set()
    for it in items:
        parts = it["path"].split(" > ")
        for k in range(2, len(parts)):
            pre = " > ".join(parts[:k])
            if pre not in seen:
                seen.add(pre)
                out.append({"path": pre, "cmd": "", "sc": ""})
        out.append({"path": it["path"], "cmd": it["cmd"], "sc": norm_sc(shortcut(it["key"], it["mods"]))})
    return out


def align(zh, en):
    """Shortcut anchors first (longest chain of exact shortcut matches in menu order); between two anchors the
    lines are paired by position only when both sides have the same count. Everything else is left unpaired:
    the export omits some commands and adds submenu headers, so a guess there is usually off by one."""
    cand = [(i, j) for i, z in enumerate(zh) if z["sc"] for j, e in enumerate(en) if e["sc"] == z["sc"]]
    best = []                                  # longest chain increasing in both i and j
    for i, j in cand:
        chain = max((c for c in best if c[-1][0] < i and c[-1][1] < j), key=len, default=[])
        best.append(chain + [(i, j)])
    chain = max(best, key=len, default=[])
    pairs = []
    prev = (-1, -1)
    for a in chain + [(len(zh), len(en))]:
        gz, ge = range(prev[0] + 1, a[0]), range(prev[1] + 1, a[1])
        if len(gz) == len(ge):
            pairs += [(zh[i], en[j], "between") for i, j in zip(gz, ge)]
        if a[0] < len(zh):
            pairs.append((zh[a[0]], en[a[1]], "shortcut"))
        prev = a
    return pairs


def main():
    review = "--review" in sys.argv
    lines = (RAW / "shortcuts_zh_TW.txt").read_text(encoding="utf-8").splitlines()
    menu = [x for x in lines[lines.index("選單指令") + 1:] if x.strip()]
    items = json.loads((HERE / "menu-index.json").read_text(encoding="utf-8"))["items"]
    # cut the Chinese list at the top-level headers (first occurrence after the previous one)
    cuts, pos = [], 0
    for en, zh in TOPS:
        k = menu.index(zh, pos)
        cuts.append(k)
        pos = k + 1
    rows = []
    for t, (en_top, zh_top) in enumerate(TOPS):
        seg = menu[cuts[t] + 1:(cuts[t + 1] if t + 1 < len(cuts) else len(menu))]
        zh = []
        for line in seg:
            lab, sc = split_label(line)
            zh.append({"zh": lab, "sc": norm_sc(sc), "raw": line})
        en = nodes_for([it for it in items if it["top"] == en_top])
        rows.append({"zh": zh_top.split("(")[0], "en_path": en_top, "cmd": "", "shortcut": "", "anchor": "top"})
        for z, e, anchor in align(zh, en):
            if z["zh"].startswith("其他"):     # group headers of the shortcut-only section, not commands
                continue
            rows.append({"zh": z["zh"], "en_path": e["path"], "cmd": e["cmd"], "shortcut": e["sc"].replace("+", "+") if e["sc"] else "",
                         "anchor": anchor})
    src = "Illustrator 28.0 zh_TW, Edit > Keyboard Shortcuts > Export Text (index/raw/shortcuts_zh_TW.txt)"
    with open(HERE / "terms_zh.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, ["zh", "en_path", "cmd", "shortcut", "anchor", "source"])
        w.writeheader()
        for r in rows:
            w.writerow({**r, "source": src})
    if review:
        for r in rows:
            print(f"{r['anchor']:<8} {r['zh']:<24} {r['en_path']:<60} {r['cmd']}")
    a = {}
    for r in rows:
        a[r["anchor"]] = a.get(r["anchor"], 0) + 1
    print(f"{len(rows)} pairs ({', '.join(f'{k} {v}' for k, v in sorted(a.items()))}) -> index/terms_zh.csv")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
