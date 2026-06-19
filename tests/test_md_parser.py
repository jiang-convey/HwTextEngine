import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from hwtext.parsing.md_parser import parse, render_outline

SRC = "\n".join([
    "# 标题",
    "",
    "这是一个段落",
    "",
    "- a",
    "- b",
    "  - b1",
    "",
    "```py",
    "code()",
    "```",
    "",
    "$$",
    "x = 1",
    "$$",
])


class TestMarkdownParser(unittest.TestCase):
    def test_top_level_block_types(self):
        doc = parse(SRC)
        types = [c.type for c in doc.children]
        self.assertEqual(types, ["heading", "paragraph", "list", "code", "math"])

    def test_heading_level_and_text(self):
        h = parse(SRC).children[0]
        self.assertEqual(h.level, 1)
        self.assertEqual(h.text, "标题")

    def test_nested_list_recursion(self):
        lst = parse(SRC).children[2]
        self.assertEqual(len(lst.children), 2)            # a, b
        nested = lst.children[1].children                 # b 的子列表
        self.assertEqual(len(nested), 1)
        self.assertEqual(nested[0].type, "list")
        self.assertEqual(nested[0].children[0].text, "b1")

    def test_fence_and_math_payload(self):
        doc = parse(SRC)
        code = doc.children[3]
        math = doc.children[4]
        self.assertEqual(code.text, "code()")
        self.assertEqual(math.text, "x = 1")

    def test_render_outline_is_tree(self):
        outline = render_outline(parse(SRC))
        self.assertIn("H1: 标题", outline)
        self.assertIn("list", outline)
        self.assertIn("item: b1", outline)


if __name__ == "__main__":
    unittest.main()
