"""二叉最小堆（优先队列）——从零实现，用数组表示完全二叉树。

知识点
    堆 / 优先队列、完全二叉树的数组表示、上浮（sift-up）/ 下沉（sift-down）。
应用
    Huffman 建树时每步都要取出当前频率最小的两个结点——正是最小优先队列。
    这里手写而非用 ``heapq``，以体现底层实现。

数组表示
    结点 i 的左右孩子为 2i+1 / 2i+2，父结点为 (i-1)//2。
复杂度
    push / pop 均 O(log n)，peek O(1)，heapify O(n)。
"""
from typing import Any, Callable, Iterable, List, Optional


class MinHeap:
    """支持自定义 ``key`` 的二叉最小堆。"""

    def __init__(self, key: Optional[Callable[[Any], Any]] = None) -> None:
        self._data: List[Any] = []
        self._key = key if key is not None else (lambda x: x)

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)

    def peek(self) -> Any:
        if not self._data:
            raise IndexError("peek from empty heap")
        return self._data[0]

    def push(self, item: Any) -> None:
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def pop(self) -> Any:
        """弹出并返回最小元素。"""
        data = self._data
        if not data:
            raise IndexError("pop from empty heap")
        top = data[0]
        last = data.pop()
        if data:                         # 把末尾移到堆顶再下沉
            data[0] = last
            self._sift_down(0)
        return top

    # --- 内部：比较与调整 --------------------------------------------------
    def _less(self, i: int, j: int) -> bool:
        return self._key(self._data[i]) < self._key(self._data[j])

    def _sift_up(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self._less(i, parent):
                self._data[i], self._data[parent] = self._data[parent], self._data[i]
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        n = len(self._data)
        while True:
            left, right, smallest = 2 * i + 1, 2 * i + 2, i
            if left < n and self._less(left, smallest):
                smallest = left
            if right < n and self._less(right, smallest):
                smallest = right
            if smallest == i:
                break
            self._data[i], self._data[smallest] = self._data[smallest], self._data[i]
            i = smallest

    @classmethod
    def heapify(cls, items: Iterable[Any],
                key: Optional[Callable[[Any], Any]] = None) -> "MinHeap":
        """自底向上 O(n) 建堆。"""
        h = cls(key=key)
        h._data = list(items)
        for i in range(len(h._data) // 2 - 1, -1, -1):
            h._sift_down(i)
        return h
