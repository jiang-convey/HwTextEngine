import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from hwtext.compress.heap import MinHeap


class TestMinHeap(unittest.TestCase):
    def test_pop_in_sorted_order(self):
        h = MinHeap()
        data = [5, 3, 8, 1, 9, 2, 7, 3]
        for x in data:
            h.push(x)
        out = [h.pop() for _ in range(len(data))]
        self.assertEqual(out, sorted(data))

    def test_custom_key(self):
        h = MinHeap(key=lambda t: t[1])
        for item in [("a", 3), ("b", 1), ("c", 2)]:
            h.push(item)
        self.assertEqual(h.pop(), ("b", 1))
        self.assertEqual(h.pop(), ("c", 2))

    def test_heapify(self):
        h = MinHeap.heapify([4, 2, 6, 1, 3])
        self.assertEqual(h.peek(), 1)
        self.assertEqual([h.pop() for _ in range(5)], [1, 2, 3, 4, 6])

    def test_empty_errors(self):
        h = MinHeap()
        self.assertFalse(h)
        with self.assertRaises(IndexError):
            h.pop()
        with self.assertRaises(IndexError):
            h.peek()


if __name__ == "__main__":
    unittest.main()
