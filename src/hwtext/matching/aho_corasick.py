"""Aho–Corasick 多模式串匹配自动机——从零实现，无外部依赖。

知识点
    字典树（Trie）、KMP 失配思想在多模式上的推广、BFS（层序）构建失配指针、
    自动机一次扫描同时匹配所有模式。
应用
    一遍扫描课程公告正文，同时命中「作业 / 习题 / 截止 / deadline / 第N题 /
    页 / page」等一大批关键词——这正是 Aho–Corasick 的典型场景。

复杂度
    构建 O(Σ|p_i|)；扫描 O(n + 命中数)。``collections.deque`` 仅作为通用
    队列容器（BFS 用），自动机本身完全手写。
"""
from collections import deque
from typing import Dict, Iterable, List, NamedTuple


class Match(NamedTuple):
    """一次命中：``text[start:end] == pattern``。"""
    start: int
    end: int
    pattern: str


class _Node:
    __slots__ = ("children", "fail", "out")

    def __init__(self) -> None:
        self.children: Dict[str, "_Node"] = {}
        self.fail: "_Node" = None        # type: ignore[assignment]
        self.out: List[str] = []         # 在此节点结束的模式串


class AhoCorasick:
    """多模式串自动机：``AhoCorasick(patterns).search(text)``。"""

    def __init__(self, patterns: Iterable[str]) -> None:
        # 去重保序：相同关键词只插一次
        seen = set()
        self.patterns: List[str] = []
        for p in patterns:
            if p and p not in seen:
                seen.add(p)
                self.patterns.append(p)
        self.root = _Node()
        self._build_trie()
        self._build_fail_links()

    # --- 1) 建字典树 -------------------------------------------------------
    def _build_trie(self) -> None:
        for pat in self.patterns:
            node = self.root
            for ch in pat:
                node = node.children.setdefault(ch, _Node())
            node.out.append(pat)

    # --- 2) BFS 建失配指针 + 合并 output ----------------------------------
    def _build_fail_links(self) -> None:
        q: deque = deque()
        self.root.fail = self.root
        # 第一层：失配指针一律指向根
        for child in self.root.children.values():
            child.fail = self.root
            q.append(child)
        # 其余层：层序处理，父节点的 fail 已就绪
        while q:
            cur = q.popleft()
            for ch, child in cur.children.items():
                f = cur.fail
                # 沿失配链找一个有 ch 出边的祖先
                while f is not self.root and ch not in f.children:
                    f = f.fail
                child.fail = f.children.get(ch, self.root)
                if child.fail is child:          # 仅作安全兜底
                    child.fail = self.root
                # 把失配节点能识别的模式并入本节点（后缀闭包）
                child.out = child.out + child.fail.out
                q.append(child)

    # --- 3) 扫描文本 -------------------------------------------------------
    def search(self, text: str) -> List[Match]:
        """返回所有命中（按结束位置自然有序）。"""
        matches: List[Match] = []
        node = self.root
        for i, ch in enumerate(text):
            # 失配则顺着 fail 链回退，直到能走 ch 或回到根
            while node is not self.root and ch not in node.children:
                node = node.fail
            node = node.children.get(ch, self.root)
            for pat in node.out:
                end = i + 1
                matches.append(Match(end - len(pat), end, pat))
        return matches

    def count(self, text: str) -> Dict[str, int]:
        """每个模式命中的次数。"""
        tally: Dict[str, int] = {p: 0 for p in self.patterns}
        for m in self.search(text):
            tally[m.pattern] += 1
        return tally
