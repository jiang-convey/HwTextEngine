"""字符串匹配与动态规划子包。

- :mod:`kmp`          —— KMP 单模式匹配（失配函数）
- :mod:`aho_corasick` —— Trie + Aho-Corasick 多模式自动机（BFS 失配指针）
- :mod:`edit_distance`—— Levenshtein 编辑距离 DP（滚动数组 + 候选排序）
"""
from .kmp import build_failure, find_all, find_first, contains
from .aho_corasick import AhoCorasick, Match
from .edit_distance import edit_distance, edit_distance_table, rank_candidates

__all__ = [
    "build_failure", "find_all", "find_first", "contains",
    "AhoCorasick", "Match",
    "edit_distance", "edit_distance_table", "rank_candidates",
]
