import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from hwtext.matching.aho_corasick import AhoCorasick


class TestAhoCorasick(unittest.TestCase):
    def test_classic_ushers(self):
        ac = AhoCorasick(["he", "she", "his", "hers"])
        found = {m.pattern for m in ac.search("ushers")}
        self.assertEqual(found, {"she", "he", "hers"})
        self.assertNotIn("his", found)

    def test_positions(self):
        ac = AhoCorasick(["he", "she", "hers"])
        ms = ac.search("ushers")
        for m in ms:
            self.assertEqual("ushers"[m.start:m.end], m.pattern)

    def test_counts(self):
        ac = AhoCorasick(["ab", "abc"])
        tally = ac.count("abcabc")
        self.assertEqual(tally["ab"], 2)
        self.assertEqual(tally["abc"], 2)

    def test_dedup_and_empty(self):
        ac = AhoCorasick(["x", "x", "", "y"])
        self.assertEqual(ac.patterns, ["x", "y"])
        self.assertEqual(ac.search("zzz"), [])

    def test_overlapping_via_fail_links(self):
        # "作业" 与 "业" 都应命中（业 借失配指针在 作业 内部被识别）
        ac = AhoCorasick(["作业", "业"])
        found = {m.pattern for m in ac.search("本周作业")}
        self.assertEqual(found, {"作业", "业"})


if __name__ == "__main__":
    unittest.main()
