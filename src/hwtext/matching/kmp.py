"""KMP 字符串匹配算法（Knuth–Morris–Pratt）——从零实现，无外部依赖。

知识点
    字符串模式匹配、失配函数（部分匹配表 / 最长公共真前后缀）。
应用
    在教材纯文本里定位「习题 3.2 / Exercise 3.2 / 第 5 题」这类题号标记，
    朴素匹配最坏 O(n·m)，KMP 用失配函数把匹配降到 O(n+m)。

复杂度
    预处理 O(m)，匹配 O(n)，总 O(n+m)；额外空间 O(m)。
"""
from typing import List


def build_failure(pattern: str) -> List[int]:
    """构造失配函数 ``fail``。

    ``fail[i]`` = 子串 ``pattern[:i+1]`` 的「最长真前缀且同时是真后缀」的长度。
    匹配失败时可据此把模式整体右移，避免回退主串指针。
    """
    m = len(pattern)
    fail = [0] * m
    k = 0  # 当前已匹配的最长前后缀长度
    for i in range(1, m):
        # 失配则沿失配链回退到次长的可复用前缀
        while k > 0 and pattern[i] != pattern[k]:
            k = fail[k - 1]
        if pattern[i] == pattern[k]:
            k += 1
        fail[i] = k
    return fail


def find_all(text: str, pattern: str) -> List[int]:
    """返回 ``pattern`` 在 ``text`` 中所有出现的起始下标（**含重叠**出现）。

    命中后借失配函数把 ``k`` 回退到 ``fail[k-1]`` 继续匹配，因此像 ``aa`` 在
    ``aaaa`` 中会报告 ``[0, 1, 2]`` 这样的重叠位置。
    约定：空模式返回 ``[]``（不匹配任何位置），避免「空串到处匹配」的歧义。
    """
    if not pattern:
        return []
    fail = build_failure(pattern)
    res: List[int] = []
    k = 0
    n, m = len(text), len(pattern)
    for i in range(n):
        while k > 0 and text[i] != pattern[k]:
            k = fail[k - 1]
        if text[i] == pattern[k]:
            k += 1
        if k == m:                       # 命中一次
            res.append(i - m + 1)
            k = fail[k - 1]              # 借失配函数继续找下一处
    return res


def find_first(text: str, pattern: str) -> int:
    """返回首次出现的起始下标；未找到返回 ``-1``。"""
    if not pattern:
        return -1
    fail = build_failure(pattern)
    k = 0
    m = len(pattern)
    for i, ch in enumerate(text):
        while k > 0 and ch != pattern[k]:
            k = fail[k - 1]
        if ch == pattern[k]:
            k += 1
        if k == m:
            return i - m + 1
    return -1


def contains(text: str, pattern: str) -> bool:
    """``pattern`` 是否为 ``text`` 的子串。"""
    return find_first(text, pattern) != -1
