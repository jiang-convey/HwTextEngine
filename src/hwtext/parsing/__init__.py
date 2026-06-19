"""解析子包：把作业文本拆成可分析的结构。

- :mod:`tokenizer`     —— 有限状态机：标记「代码」区域（围栏 / 行内）
- :mod:`bracket_stack` —— 栈：定界符 / 括号配对校验
- :mod:`delim_fix`     —— \\[ \\] \\( \\) -> $$ $（跳过代码）
- :mod:`md_parser`     —— 递归下降：Markdown -> 抽象语法树（AST）
"""
from .tokenizer import protected_mask, segments
from .bracket_stack import check_brackets, BracketReport, BracketError
from .delim_fix import normalize_delims
from .md_parser import parse, render_outline, Node

__all__ = [
    "protected_mask", "segments",
    "check_brackets", "BracketReport", "BracketError",
    "normalize_delims",
    "parse", "render_outline", "Node",
]
