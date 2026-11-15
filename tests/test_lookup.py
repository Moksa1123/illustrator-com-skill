"""Offline self-tests for the lookup layer (no Illustrator, no network, stdlib only).

    python -m unittest discover -s tests -p "test_*.py"

Covers: ai_api.py queries (English and Chinese), the zh_TW glossaries, the data files the SKILL.md Sources table
describes, the numbers in SKILL.md (tools/check_numbers.py), the eval answer key, and the SOP section headings.
Tests that need index/ai-dom.json (built locally, not shipped) or index/raw/ (local app exports) skip without them.
"""
import csv
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
INDEX = SKILL / "index"
HAS_DOM = (INDEX / "ai-dom.json").exists()
RAW_ZH = INDEX / "raw" / "shortcuts_zh_TW.txt"


def api(*args):
    r = subprocess.run([sys.executable, str(INDEX / "ai_api.py"), *args], capture_output=True, text=True,
                       encoding="utf-8", cwd=SKILL)
    return r.stdout + r.stderr


def load(rel):
    return json.loads((SKILL / rel).read_text(encoding="utf-8"))


def rows(rel):
    with open(SKILL / rel, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


MENU = {i["cmd"]: i for i in load("index/menu-index.json")["items"]}


@unittest.skipUnless(HAS_DOM, "index/ai-dom.json not built on this machine")
class TestApiDom(unittest.TestCase):
    def test_find_english(self):
        self.assertIn("createOutline", api("find", "createOutline"))

    def test_find_chinese_gradient(self):
        self.assertIn("Gradient", api("find", "漸層"))

    def test_find_chinese_points_to_effect(self):
        out = api("find", "陰影")
        self.assertIn("Drop Shadow", out)
        self.assertIn("ai_api.py effect", out)

    def test_class_and_enum(self):
        self.assertIn("textFrames", api("class", "Document"))
        self.assertIn("BlendModes.MULTIPLY", api("enum", "BlendModes"))

    def test_member_unverified_flag(self):
        self.assertIn('"verified": false', api("member", "GraphItem.opacity"))

    def test_stats(self):
        out = api("stats")
        self.assertRegex(out, r"Illustrator \d+\.\d+")
        self.assertRegex(out, r"classes: \d+")


class TestApiMenuEffect(unittest.TestCase):
    def test_menu_english(self):
        self.assertIn("app.executeMenuCommand('outline')", api("menu", "Create Outlines"))

    def test_menu_chinese(self):
        cases = {"建立外框": "'outline'", "外框筆畫": "'OffsetPath v22'", "剪裁遮色片": "'makeMask'",
                 "擴充外觀": "'expandStyle'", "組成群組": "'group'"}
        for zh, cmd in cases.items():
            with self.subTest(zh=zh):
                self.assertIn(cmd, api("menu", zh))

    def test_menu_mixed_words(self):
        out = api("menu", "外框", "Stroke")
        self.assertIn("OffsetPath v22", out)

    def test_effect_english(self):
        self.assertIn("Adobe Drop Shadow", api("effect", "Drop Shadow"))

    def test_effect_chinese(self):
        cases = {"陰影": "Adobe Drop Shadow", "羽化": "Adobe Fuzzy Mask", "圓角": "Adobe Round Corners",
                 "高斯模糊": "Adobe PSL Gaussian Blur", "縮攏與膨脹": "Adobe Punk and Bloat"}
        for zh, name in cases.items():
            with self.subTest(zh=zh):
                self.assertIn(name, api("effect", zh))

    def test_unknown_chinese_finds_nothing(self):
        self.assertEqual(api("menu", "不存在的詞彙").strip(), "")


class TestGlossaries(unittest.TestCase):
    def test_glossary_rows(self):
        for r in rows("index/glossary_zh.csv"):
            with self.subTest(zh=r["zh"]):
                self.assertIn(r["confidence"], ("ui-string", "inferred"))
                self.assertTrue(r["source"])
                if r["cmd"]:
                    self.assertIn(r["cmd"], MENU)
                    self.assertEqual(MENU[r["cmd"]]["path"], r["en_path"])
                self.assertTrue(r["cmd"] or r["dom_words"] or r["en_path"])

    @unittest.skipUnless(RAW_ZH.exists(), "index/raw/shortcuts_zh_TW.txt not on this machine")
    def test_ui_strings_are_real_labels(self):
        raw = RAW_ZH.read_text(encoding="utf-8")
        for r in rows("index/glossary_zh.csv"):
            if r["confidence"] == "ui-string":
                with self.subTest(zh=r["zh"]):
                    self.assertIn(r["zh"], raw)

    def test_terms_rows(self):
        T = rows("index/terms_zh.csv")
        self.assertGreater(len(T), 100)
        for r in T:
            with self.subTest(zh=r["zh"], en=r["en_path"]):
                self.assertIn(r["anchor"], ("top", "shortcut", "between"))
                if r["cmd"]:
                    self.assertEqual(MENU[r["cmd"]]["path"], r["en_path"])

    def test_shortcut_anchors_agree(self):
        # anchor=shortcut rows: the shortcut stored is the command's own shortcut in menu-index.json
        for r in rows("index/terms_zh.csv"):
            if r["anchor"] == "shortcut":
                with self.subTest(zh=r["zh"]):
                    self.assertTrue(r["shortcut"])
                    self.assertTrue(MENU[r["cmd"]]["key"])

    @unittest.skipUnless(RAW_ZH.exists(), "index/raw/shortcuts_zh_TW.txt not on this machine")
    def test_terms_rebuild_is_stable(self):
        before = (INDEX / "terms_zh.csv").read_bytes()
        subprocess.run([sys.executable, str(INDEX / "build_zh_terms.py")], capture_output=True, cwd=SKILL, check=True)
        self.assertEqual(before, (INDEX / "terms_zh.csv").read_bytes())


class TestData(unittest.TestCase):
    def test_coverage_matches_menu(self):
        cov = load("tests/coverage.json")["rows"]
        self.assertEqual({r["cmd"] for r in cov}, set(MENU))
        for r in cov:
            with self.subTest(cmd=r["cmd"]):
                self.assertIn(r["status"], ("✅", "n/a", "blocked"))
                self.assertTrue(r.get("how"))

    def test_effects_have_xml(self):
        for e in load("presets/effects.json")["effects"]:
            with self.subTest(name=e["name"]):
                self.assertTrue(e["ok"])
                if e["menu"] == "Effect > Effect Gallery":   # a gallery of filters: run through the menu, no single XML
                    self.assertIn(e["cmd"], MENU)
                    continue
                self.assertRegex(e["xml"], r'^<LiveEffect name="[^"]+">')
                self.assertTrue(e["menu"].startswith("Effect > "))

    def test_sizes_have_source_and_confidence(self):
        for s in load("presets/sizes.json")["sizes"]:
            with self.subTest(id=s.get("id")):
                self.assertIn(s.get("confidence"), ("official", "widely-cited"))
                self.assertTrue(s.get("source") or s.get("sources"))

    def test_pending_csv(self):
        P = rows("data/pending.csv")
        self.assertTrue(P)
        for r in P:
            self.assertRegex(r["date"], r"^\d{4}-\d\d-\d\d$")
            self.assertTrue(r["question"] and r["why_not_found"] and r["asked_by"])


class TestSkillMd(unittest.TestCase):
    TEXT = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_numbers_match_data(self):
        r = subprocess.run([sys.executable, str(SKILL / "tools" / "check_numbers.py")], capture_output=True,
                           text=True, encoding="utf-8", cwd=SKILL)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_sections_in_order(self):
        heads = re.findall(r"^## (\S+)", self.TEXT, re.M)
        want = ["Sources", "Usage", "Routing", "Tasks", "Verify", "Maintenance"]
        self.assertEqual([h for h in heads if h in want], want)

    def test_lookup_first_rule_opens_routing(self):
        routing = self.TEXT.split("## Routing", 1)[1]
        self.assertTrue(routing.lstrip().startswith("**Look it up first, never answer from memory.**"))
        self.assertIn("data/pending.csv", routing[:600])

    def test_frontmatter(self):
        fm = self.TEXT.split("---", 2)[1]
        self.assertRegex(fm, r"(?m)^user-invocable: true$")
        self.assertRegex(fm, r"(?m)^name: illustrator-com$")

    def test_size(self):
        self.assertLessEqual(len(self.TEXT.encode("utf-8")), 20 * 1024)

    def test_paths_exist(self):
        for p in sorted(set(re.findall(r"`((?:lib|index|tools|tests|presets|data|evals|examples)/[\w./-]+\.\w+)`", self.TEXT))):
            if p == "index/ai-dom.json" and not HAS_DOM:
                continue
            with self.subTest(path=p):
                self.assertTrue((SKILL / p).exists(), p)


class TestEvals(unittest.TestCase):
    def test_answer_key_passes_grader(self):
        sys.path.insert(0, str(SKILL / "evals"))
        import grade
        cases = grade.load_cases()
        self.assertGreaterEqual(len(cases), 10)
        for c in cases:
            with self.subTest(id=c["id"]):
                self.assertTrue(grade.correct(c, c["answer"]))
                self.assertFalse(grade.correct(c, "I don't know"))

    def test_menu_answers_come_from_data(self):
        for c in json.loads((SKILL / "evals" / "cases.json").read_text(encoding="utf-8"))["cases"]:
            m = re.search(r"executeMenuCommand\('([^']+)'\)", c["answer"])
            if m:
                with self.subTest(id=c["id"]):
                    self.assertIn(m.group(1), MENU)


if __name__ == "__main__":
    unittest.main()
