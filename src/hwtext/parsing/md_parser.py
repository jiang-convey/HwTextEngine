"""Markdown 块级结构的**递归下降**解析器：源码 -> 抽象语法树（AST）。

知识点
    递归下降解析、树（AST）、递归（嵌套列表借助缩进递归构建）。
应用
    把整理好的作业答案解析成块树（标题 / 代码 / 公式 / 列表 / 引用 / 段落），
    便于统计结构、定位代码与公式区域，再交给渲染器。

文法（EBNF 近似）
    document   := block*
    block      := heading | fence | math_block | blockquote | list | paragraph
    heading    := '#'{1..6} ' ' text
    fence      := '```' ... '```'
    math_block := '$$' ... '$$'
    blockquote := ('>' line)+
    list       := item+      ;  item := marker text sublist?      # sublist 递归
    paragraph  := line+ (直到空行或其它块起始)

边界
    面向作业文档的实用子集，非 CommonMark 全量实现（行内强调/链接不展开，
    只保留为文本）。这些边界在 docs/DESIGN.md 中已注明。
"""
from typing import List, Optional

DOC = "document"
HEADING = "heading"
FENCE = "code"
MATH = "math"
QUOTE = "quote"
LIST = "list"
ITEM = "item"
PARA = "paragraph"


class Node:
    """AST 结点。``children`` 构成树；``level`` 记标题层级或列表缩进。"""
    __slots__ = ("type", "text", "children", "level")

    def __init__(self, type: str, text: str = "",
                 children: Optional[List["Node"]] = None, level: int = 0) -> None:
        self.type = type
        self.text = text
        self.children = children if children is not None else []
        self.level = level

    def __repr__(self) -> str:
        head = self.text[:20] + ("…" if len(self.text) > 20 else "")
        return "Node(%s, %r, kids=%d)" % (self.type, head, len(self.children))


# --- 单行分类的小工具（手写，不用正则，保持「算法零依赖」）-----------------
def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _is_blank(line: str) -> bool:
    return line.strip() == ""


def _heading_level(stripped: str) -> int:
    """行（已去前导空格）是标题则返回 1..6，否则 0。"""
    k = 0
    while k < len(stripped) and stripped[k] == "#":
        k += 1
    if 1 <= k <= 6 and k < len(stripped) and stripped[k] == " ":
        return k
    return 0


def _list_item(line: str):
    """是列表项则返回 ``(indent, content)``，否则 ``None``。支持 - * + 和 1. 1)。"""
    indent = _indent(line)
    s = line[indent:]
    if len(s) >= 2 and s[0] in "-*+" and s[1] == " ":
        return indent, s[2:].strip()
    j = 0
    while j < len(s) and s[j].isdigit():
        j += 1
    if 0 < j < len(s) and s[j] in ".)" and j + 1 < len(s) and s[j + 1] == " ":
        return indent, s[j + 2:].strip()
    return None


class _Parser:
    def __init__(self, src: str) -> None:
        self.lines = src.split("\n")
        self.i = 0

    def _line(self) -> str:
        return self.lines[self.i]

    def _eof(self) -> bool:
        return self.i >= len(self.lines)

    # 顶层：反复识别并下降到对应的块解析函数
    def parse(self) -> Node:
        doc = Node(DOC)
        while not self._eof():
            line = self._line()
            if _is_blank(line):
                self.i += 1
                continue
            s = line.lstrip(" ")
            if s.startswith("```"):
                doc.children.append(self._fence())
            elif s.strip() == "$$":
                doc.children.append(self._math())
            elif _heading_level(s):
                lvl = _heading_level(s)
                doc.children.append(Node(HEADING, s[lvl + 1:].strip(), level=lvl))
                self.i += 1
            elif s.startswith(">"):
                doc.children.append(self._quote())
            elif _list_item(line):
                doc.children.append(self._list(_list_item(line)[0]))
            else:
                doc.children.append(self._paragraph())
        return doc

    def _fence(self) -> Node:
        self.i += 1                       # 跳过开栏 ```
        buf: List[str] = []
        while not self._eof() and self._line().strip() != "```":
            buf.append(self._line())
            self.i += 1
        if not self._eof():
            self.i += 1                   # 跳过闭栏
        return Node(FENCE, "\n".join(buf))

    def _math(self) -> Node:
        self.i += 1
        buf: List[str] = []
        while not self._eof() and self._line().strip() != "$$":
            buf.append(self._line())
            self.i += 1
        if not self._eof():
            self.i += 1
        return Node(MATH, "\n".join(buf))

    def _quote(self) -> Node:
        buf: List[str] = []
        while not self._eof() and self._line().lstrip(" ").startswith(">"):
            s = self._line().lstrip(" ")[1:]
            buf.append(s[1:] if s.startswith(" ") else s)
            self.i += 1
        return Node(QUOTE, "\n".join(buf))

    def _list(self, indent: int) -> Node:
        node = Node(LIST, level=indent)
        while not self._eof():
            line = self._line()
            if _is_blank(line):
                break
            li = _list_item(line)
            if not li:
                break
            ind, content = li
            if ind < indent:              # 回到更外层，交还上层处理
                break
            if ind > indent:              # 没有同级父项的更深项：作为子列表递归
                if node.children:
                    node.children[-1].children.append(self._list(ind))
                    continue
                break
            # 同级列表项
            self.i += 1
            item = Node(ITEM, content, level=indent)
            nxt = _list_item(self._line()) if not self._eof() else None
            if nxt and nxt[0] > indent:   # 紧跟更深缩进 -> 递归建子列表
                item.children.append(self._list(nxt[0]))
            node.children.append(item)
        return node

    def _paragraph(self) -> Node:
        buf: List[str] = []
        while not self._eof():
            line = self._line()
            if _is_blank(line):
                break
            s = line.lstrip(" ")
            if (s.startswith("```") or s.strip() == "$$" or _heading_level(s)
                    or s.startswith(">") or _list_item(line)):
                break
            buf.append(line.strip())
            self.i += 1
        return Node(PARA, " ".join(buf))


def parse(src: str) -> Node:
    """解析 Markdown 文本，返回 ``document`` 根结点。"""
    return _Parser(src).parse()


def render_outline(node: Node, depth: int = 0) -> str:
    """把 AST 渲染成缩进大纲（用于 CLI 展示树结构）。"""
    lines: List[str] = []
    if node.type != DOC:
        lines.append("  " * depth + "- " + _label(node))
    child_depth = depth if node.type == DOC else depth + 1
    for c in node.children:
        sub = render_outline(c, child_depth)
        if sub:
            lines.append(sub)
    return "\n".join(lines)


def _label(node: Node) -> str:
    def clip(t: str, k: int = 40) -> str:
        t = t.replace("\n", " ")
        return t[:k] + ("…" if len(t) > k else "")
    if node.type == HEADING:
        return "H%d: %s" % (node.level, clip(node.text))
    if node.type == FENCE:
        ln = node.text.count("\n") + 1 if node.text else 0
        return "code[%d 行]" % ln
    if node.type == MATH:
        return "math: %s" % clip(node.text)
    if node.type == ITEM:
        return "item: %s" % clip(node.text)
    if node.type == LIST:
        return "list"
    if node.type in (PARA, QUOTE):
        return "%s: %s" % (node.type, clip(node.text))
    return node.type
