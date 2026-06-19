"""压缩子包：手写最小堆 + Huffman 编码。

- :mod:`heap`    —— 二叉最小堆（优先队列）
- :mod:`huffman` —— 贪心 + 二叉树构造前缀码，无损编/解码与压缩比统计
"""
from .heap import MinHeap
from .huffman import (
    char_freq, build_tree, build_codes, encode, decode, compress_report,
)

__all__ = [
    "MinHeap",
    "char_freq", "build_tree", "build_codes", "encode", "decode",
    "compress_report",
]
