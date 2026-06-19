"""文档分析：解析结构（AST）+ Huffman 压缩比统计。

    递归下降（:mod:`md_parser`）—— 把答案解析成块树并给出大纲
    Huffman（:mod:`huffman`）     —— 统计字符频率，报告无损压缩比
"""
from typing import Dict

from ..compress.huffman import compress_report
from ..parsing.md_parser import parse, render_outline


def analyze(src: str) -> Dict:
    """返回 ``{ast, outline, compress}``。"""
    ast = parse(src)
    return {"ast": ast, "outline": render_outline(ast),
            "compress": compress_report(src)}
