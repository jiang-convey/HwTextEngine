"""Huffman 编码——贪心 + 二叉树，从零实现（最小堆来自 :mod:`heap`）。

知识点
    贪心算法、二叉树、前缀码、优先队列（最小堆）。
应用
    统计「提取出的题目 / 整理后的答案」文本的字符频率并做无损压缩，报告压缩比，
    作为「算法应用工具」里的一个文本分析功能。

算法
    1) 统计字符频率；2) 每个字符建叶子入堆；3) 反复取两个最小频率结点合并成
    父结点（频率求和）再入堆，直到只剩一个根；4) 左 0 右 1 得到每个字符的前缀码。
复杂度
    建树 O(k log k)（k 为不同字符数）；编 / 解码 O(n)。
"""
from typing import Dict, Optional, Tuple

from .heap import MinHeap


class _HNode:
    __slots__ = ("freq", "char", "left", "right", "order")

    def __init__(self, freq: int, char: Optional[str] = None,
                 left: Optional["_HNode"] = None,
                 right: Optional["_HNode"] = None, order: int = 0) -> None:
        self.freq = freq
        self.char = char          # 叶子才有字符；内部结点为 None
        self.left = left
        self.right = right
        self.order = order        # 入堆序号，用于稳定的并列处理（结果可复现）


def char_freq(text: str) -> Dict[str, int]:
    """统计字符频率。"""
    freq: Dict[str, int] = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    return freq


def build_tree(freq: Dict[str, int]) -> Optional[_HNode]:
    """由频率表构造 Huffman 树，返回根结点（空输入返回 ``None``）。"""
    if not freq:
        return None
    order = 0
    # key=(频率, 入堆序) 保证并列时确定性，编码结果可复现
    heap = MinHeap(key=lambda nd: (nd.freq, nd.order))
    for ch in sorted(freq):              # 排序后入堆，进一步保证确定性
        heap.push(_HNode(freq[ch], ch, order=order))
        order += 1
    if len(heap) == 1:                   # 只有一种字符：包一层，保证码长 >= 1
        only = heap.pop()
        return _HNode(only.freq, None, left=only, order=order)
    while len(heap) > 1:
        a = heap.pop()
        b = heap.pop()
        heap.push(_HNode(a.freq + b.freq, None, left=a, right=b, order=order))
        order += 1
    return heap.pop()


def build_codes(root: Optional[_HNode]) -> Dict[str, str]:
    """前序遍历二叉树，左 0 右 1，得到字符 -> 码字。"""
    codes: Dict[str, str] = {}

    def walk(node: Optional[_HNode], prefix: str) -> None:
        if node is None:
            return
        if node.char is not None:        # 叶子
            codes[node.char] = prefix or "0"
            return
        walk(node.left, prefix + "0")
        walk(node.right, prefix + "1")

    walk(root, "")
    return codes


def encode(text: str) -> Tuple[str, Dict[str, str]]:
    """返回 ``(比特串, 码表)``。"""
    codes = build_codes(build_tree(char_freq(text)))
    bits = "".join(codes[ch] for ch in text)
    return bits, codes


def decode(bits: str, root: Optional[_HNode]) -> str:
    """沿二叉树用比特串还原文本（前缀码无歧义）。"""
    if root is None:
        return ""
    out = []
    node = root
    for b in bits:
        node = node.left if b == "0" else node.right
        if node.char is not None:
            out.append(node.char)
            node = root
    return "".join(out)


def compress_report(text: str) -> Dict[str, object]:
    """返回压缩统计：符号数、原始 / 编码比特数、压缩比、平均码长。"""
    if not text:
        return {"symbols": 0, "chars": 0, "original_bits": 0,
                "encoded_bits": 0, "ratio": 0.0, "avg_code_len": 0.0}
    bits, codes = encode(text)
    original = len(text) * 8             # 以 8 bit/字符为基线
    encoded = len(bits)
    return {
        "symbols": len(codes),
        "chars": len(text),
        "original_bits": original,
        "encoded_bits": encoded,
        "ratio": round(encoded / original, 4) if original else 0.0,
        "avg_code_len": round(encoded / len(text), 4),
    }
