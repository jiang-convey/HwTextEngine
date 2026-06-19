import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from hwtext import apps


class TestLocate(unittest.TestCase):
    TEXT = "习题3.1 关于级数\n习题3.2 这是目标题目内容\n习题3.3 其它内容"

    def test_found(self):
        r = apps.locate(self.TEXT, ["3.2"])
        p = r["problems"][0]
        self.assertTrue(p["found"])
        self.assertIn("目标题目", p["content"])
        self.assertNotIn("3.3", p["content"])       # 被下一题号截断
        self.assertEqual(r["missing"], [])

    def test_candidates_when_missing(self):
        r = apps.locate(self.TEXT, ["9.9"])
        p = r["problems"][0]
        self.assertFalse(p["found"])
        self.assertTrue(p["candidates"])
        self.assertEqual(r["missing"], ["9.9"])


class TestMine(unittest.TestCase):
    def test_detects_homework(self):
        text = "【通知】本周作业：习题3.2，请于截止周五 23:59 前提交。"
        c = apps.mine(text, "通知")
        self.assertIsNotNone(c)
        self.assertTrue(c["is_homework"])
        self.assertTrue(any("3.2" in ref for ref in c["problem_refs"]))
        self.assertIsNotNone(c["due"])

    def test_no_signal(self):
        self.assertIsNone(apps.mine("今天天气不错，随便聊聊。"))


class TestFix(unittest.TestCase):
    def test_replacements(self):
        r = apps.fix(r"解：\(x\)，矩阵 \[A\]")
        self.assertEqual(r["replacements"], 4)
        self.assertIn("$x$", r["fixed"])
        self.assertIn("$$A$$", r["fixed"])
        self.assertTrue(r["after"].ok())


class TestAnalyze(unittest.TestCase):
    def test_outline_and_compress(self):
        r = apps.analyze("# 标题\n\n- a\n- b\n")
        self.assertIn("list", r["outline"])
        self.assertGreater(r["compress"]["chars"], 0)


if __name__ == "__main__":
    unittest.main()
