"""编辑距离（Levenshtein distance）——动态规划，从零实现。

知识点
    动态规划、二维状态转移、滚动数组空间优化、最优解回溯。
应用
    题号精确匹配失败时（找不到「3.2」），按编辑距离在候选标记里给出最接近的
    若干个（如「3.1 / 3.20 / 3.12」），即仓库原有「找不到→给候选」的能力。

状态转移
    dp[i][j] = a[:i] 变成 b[:j] 的最少单字符增/删/改次数
             = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+(a[i-1]!=b[j-1]))
复杂度
    O(m·n) 时间；完整表 O(m·n) 空间，滚动数组 O(min(m,n)) 空间。
"""
from typing import List, Sequence, Tuple


def edit_distance(a: str, b: str) -> int:
    """滚动数组实现：只保留 DP 表相邻两行，空间 O(min(m, n))。"""
    if len(a) < len(b):                  # 让较短串当列，省空间
        a, b = b, a
    prev = list(range(len(b) + 1))       # i=0 行：把空串变成 b[:j] 需 j 次插入
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)         # j=0 列：删光 a[:i] 需 i 次
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur[j] = min(
                prev[j] + 1,             # 删除 a[i-1]
                cur[j - 1] + 1,          # 插入 b[j-1]
                prev[j - 1] + cost,      # 替换 / 匹配
            )
        prev = cur
    return prev[len(b)]


def edit_distance_table(a: str, b: str) -> List[List[int]]:
    """返回完整 DP 表（可用于可视化与回溯）。``dp[i][j]`` 含义见模块文档。"""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp


def rank_candidates(
    target: str, candidates: Sequence[str], top_k: int = 5
) -> List[Tuple[str, int]]:
    """按与 ``target`` 的编辑距离升序返回 ``(candidate, distance)``。

    并列时用「长度、字典序」做稳定的次级排序，便于复现实验结果。
    ``top_k <= 0`` 时返回全部。
    """
    scored = [(c, edit_distance(target, c)) for c in candidates]
    scored.sort(key=lambda t: (t[1], len(t[0]), t[0]))
    return scored if top_k <= 0 else scored[:top_k]
