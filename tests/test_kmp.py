import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from hwtext.matching.kmp import build_failure, contains, find_all, find_first


class TestKMP(unittest.TestCase):
    def test_failure_function(self):
        self.assertEqual(build_failure("ababaca"), [0, 0, 1, 2, 3, 0, 1])
        self.assertEqual(build_failure("aaaa"), [0, 1, 2, 3])
        self.assertEqual(build_failure("abc"), [0, 0, 0])

    def test_overlapping_matches(self):
        self.assertEqual(find_all("aaaa", "aa"), [0, 1, 2])
        self.assertEqual(find_all("abababab", "abab"), [0, 2, 4])

    def test_cross_check_non_overlapping_pattern(self):
        text = "习题3.1 级数；习题3.20 收敛；习题3.2 极限；又见 习题3.2 收尾"
        pat = "习题3.2"            # 无自重叠，可与 str.find 逐一比对
        ref, i = [], text.find(pat)
        while i != -1:
            ref.append(i)
            i = text.find(pat, i + 1)   # +1 也能覆盖重叠，这里恰好无重叠
        self.assertEqual(find_all(text, pat), ref)

    def test_first_and_contains(self):
        self.assertEqual(find_first("hello world", "world"), 6)
        self.assertEqual(find_first("abc", "x"), -1)
        self.assertTrue(contains("abc", "bc"))
        self.assertFalse(contains("abc", "cb"))

    def test_empty_pattern(self):
        self.assertEqual(find_all("abc", ""), [])
        self.assertEqual(find_first("abc", ""), -1)


if __name__ == "__main__":
    unittest.main()
