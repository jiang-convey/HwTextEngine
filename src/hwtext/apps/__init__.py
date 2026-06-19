"""应用层：把自实现算法串成面向作业的功能。

这里只放**纯逻辑**（吃字符串、吐数据结构）；读 PDF、打印、命令行参数等
**界面 / IO 职责放在 :mod:`hwtext.io` 与 :mod:`hwtext.cli`**，做到逻辑与界面分离。
"""
from .locate_problem import locate, locate_one, discover_ids, marker_variants
from .mine_homework import mine, mine_all, KEYWORDS
from .fix_answer import fix
from .analyze import analyze

__all__ = [
    "locate", "locate_one", "discover_ids", "marker_variants",
    "mine", "mine_all", "KEYWORDS",
    "fix", "analyze",
]
