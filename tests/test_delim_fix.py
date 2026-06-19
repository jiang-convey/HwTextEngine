import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from hwtext.parsing.delim_fix import normalize_delims
from hwtext.parsing.tokenizer import protected_mask, segments


class TestDelimFix(unittest.TestCase):
    def test_basic_rewrite(self):
        self.assertEqual(normalize_delims(r"\(x\)"), ("$x$", 2))
        self.assertEqual(normalize_delims(r"\[a+b\]"), ("$$a+b$$", 2))

    def test_skip_fenced_code(self):
        src = "```\n\\(x\\)\n```"
        out, n = normalize_delims(src)
        self.assertEqual(n, 0)
        self.assertEqual(out, src)

    def test_skip_inline_code(self):
        out, n = normalize_delims(r"`\(b\)`")
        self.assertEqual(n, 0)
        self.assertEqual(out, r"`\(b\)`")

    def test_mixed(self):
        out, n = normalize_delims(r"文 \(a\) `\(b\)` 末")
        self.assertEqual(out, r"文 $a$ `\(b\)` 末")
        self.assertEqual(n, 2)


class TestTokenizer(unittest.TestCase):
    def test_protected_mask_inline(self):
        src = "a`b`c"
        mask = protected_mask(src)
        self.assertEqual(mask, [False, True, True, True, False])

    def test_segments_roundtrip(self):
        src = "x `y` z"
        self.assertEqual("".join(t for _, t in segments(src)), src)


if __name__ == "__main__":
    unittest.main()
