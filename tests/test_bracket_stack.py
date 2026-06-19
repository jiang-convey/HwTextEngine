import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from hwtext.parsing.bracket_stack import check_brackets


class TestBracketStack(unittest.TestCase):
    def test_balanced(self):
        self.assertTrue(check_brackets("(a[b]{c})").ok())
        self.assertTrue(check_brackets(r"\(x+y\) 与 \[A\]").ok())

    def test_mismatch(self):
        r = check_brackets("(]")
        self.assertFalse(r.balanced)
        self.assertTrue(any(e.kind == "mismatch" for e in r.errors))

    def test_unclosed_open(self):
        r = check_brackets("(((")
        self.assertFalse(r.balanced)
        self.assertEqual(sum(e.kind == "unclosed_open" for e in r.errors), 3)

    def test_unmatched_close(self):
        r = check_brackets(")")
        self.assertFalse(r.balanced)
        self.assertTrue(any(e.kind == "unmatched_close" for e in r.errors))

    def test_math_parity(self):
        self.assertTrue(check_brackets("$x$ 与 $$y$$").math_balanced)
        self.assertFalse(check_brackets("$x").math_balanced)

    def test_code_is_skipped(self):
        # 行内代码里的右括号不应算作未匹配
        self.assertTrue(check_brackets("`)` 只是示例").ok())
        # 围栏代码块里的不配对括号也被忽略
        self.assertTrue(check_brackets("```\n(((\n```").ok())


if __name__ == "__main__":
    unittest.main()
