import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from hwtext.compress.huffman import (
    build_codes, build_tree, char_freq, compress_report, decode, encode,
)


class TestHuffman(unittest.TestCase):
    def test_round_trip(self):
        for text in ["abracadabra", "mississippi", "数算B 大作业 data structure"]:
            bits, _ = encode(text)
            root = build_tree(char_freq(text))
            self.assertEqual(decode(bits, root), text)

    def test_prefix_free(self):
        _, codes = encode("abracadabra")
        words = list(codes.values())
        for i, a in enumerate(words):
            for j, b in enumerate(words):
                if i != j:
                    self.assertFalse(b.startswith(a),
                                     "%r 是 %r 的前缀，违反前缀码" % (a, b))

    def test_single_symbol(self):
        bits, codes = encode("aaaa")
        self.assertEqual(codes, {"a": "0"})
        root = build_tree(char_freq("aaaa"))
        self.assertEqual(decode(bits, root), "aaaa")

    def test_compress_report(self):
        r = compress_report("aaaaaaaa")
        self.assertEqual(r["symbols"], 1)
        self.assertEqual(r["chars"], 8)
        self.assertLess(r["ratio"], 0.2)        # 高度可压缩

    def test_empty(self):
        self.assertEqual(encode(""), ("", {}))
        self.assertEqual(decode("", build_tree(char_freq(""))), "")


if __name__ == "__main__":
    unittest.main()
