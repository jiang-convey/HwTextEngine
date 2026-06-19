import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from hwtext.matching.edit_distance import (
    edit_distance, edit_distance_table, rank_candidates,
)


class TestEditDistance(unittest.TestCase):
    def test_known_values(self):
        self.assertEqual(edit_distance("kitten", "sitting"), 3)
        self.assertEqual(edit_distance("flaw", "lawn"), 2)
        self.assertEqual(edit_distance("abc", "abc"), 0)

    def test_empty(self):
        self.assertEqual(edit_distance("", "abc"), 3)
        self.assertEqual(edit_distance("abc", ""), 3)
        self.assertEqual(edit_distance("", ""), 0)

    def test_symmetry(self):
        self.assertEqual(edit_distance("sunday", "saturday"),
                         edit_distance("saturday", "sunday"))

    def test_table_corner(self):
        dp = edit_distance_table("ab", "abc")
        self.assertEqual(dp[2][3], 1)        # ab -> abc 需 1 次插入
        self.assertEqual(dp[0][3], 3)

    def test_rank_candidates(self):
        ranked = rank_candidates("3.2", ["3.1", "3.20", "3.2", "10.2"], top_k=3)
        self.assertEqual(ranked[0], ("3.2", 0))
        self.assertEqual(len(ranked), 3)
        # 距离单调不降
        dists = [d for _, d in ranked]
        self.assertEqual(dists, sorted(dists))


if __name__ == "__main__":
    unittest.main()
