"""用**栈**做定界符 / 括号的配对校验——从零实现。

知识点
    栈（后进先出 LIFO）。
应用
    渲染前校验用户 / AI 贴来的答案里 ``()`` ``[]`` ``{}`` ``\\[\\]`` ``\\(\\)``
    是否配对，以及 ``$`` / ``$$`` 数学环境是否成对，**提前报错**而不是让
    MathJax 静默崩坏、整段公式失踪。

扫描方向
    严格按文本的**自然阅读顺序从左到右**扫描：遇左定界符入栈，遇右定界符与
    栈顶配对并出栈，扫描结束栈应为空。括号匹配的自然语义方向就是阅读方向——
    先出现的左括号最后闭合，恰是栈的 LIFO 语义；反向扫描只会把问题复杂化。

复杂度
    O(n) 时间；栈深 O(嵌套层数)。代码区域借 :func:`tokenizer.protected_mask` 跳过。
"""
from typing import List, NamedTuple, Tuple

from .tokenizer import protected_mask

_PAIR = {")": "(", "]": "[", "}": "{", "\\)": "\\(", "\\]": "\\["}
_OPENERS = {"(", "[", "{", "\\(", "\\["}
_CLOSERS = set(_PAIR)
_TWO = ("\\[", "\\]", "\\(", "\\)")      # 两字符定界符，需先于单字符识别


class BracketError(NamedTuple):
    pos: int
    kind: str          # unmatched_close | mismatch | unclosed_open
    detail: str


class BracketReport(NamedTuple):
    balanced: bool         # () [] {} \[\] \(\) 是否全部配对
    math_balanced: bool    # $ / $$ 是否成对
    errors: List[BracketError]

    def ok(self) -> bool:
        return self.balanced and self.math_balanced

    def summary(self) -> str:
        if self.ok():
            return "OK：所有定界符配对正确。"
        msgs: List[str] = []
        if not self.math_balanced:
            msgs.append("数学定界符 $/$$ 不成对")
        for e in self.errors:
            msgs.append("位置 %d：%s（%s）" % (e.pos, e.detail, e.kind))
        return "；".join(msgs)


def check_brackets(src: str) -> BracketReport:
    """对 ``src`` 做定界符配对校验，返回 :class:`BracketReport`。"""
    mask = protected_mask(src)
    stack: List[Tuple[str, int]] = []
    errors: List[BracketError] = []

    i, n = 0, len(src)
    while i < n:
        if mask[i]:                      # 跳过代码
            i += 1
            continue
        two = src[i:i + 2]
        tok, step = (two, 2) if two in _TWO else (src[i], 1)
        if tok in _OPENERS:
            stack.append((tok, i))
        elif tok in _CLOSERS:
            if not stack:
                errors.append(BracketError(i, "unmatched_close",
                                           "多余的右定界符 %r" % tok))
            else:
                op, _ = stack.pop()
                if _PAIR[tok] != op:
                    errors.append(BracketError(
                        i, "mismatch",
                        "右定界符 %r 与栈顶左定界符 %r 不匹配" % (tok, op)))
        i += step

    for op, pos in stack:                # 扫描结束仍在栈里 = 未闭合
        errors.append(BracketError(pos, "unclosed_open", "未闭合的左定界符 %r" % op))

    return BracketReport(
        balanced=not errors,
        math_balanced=_check_math(src, mask),
        errors=errors,
    )


def _check_math(src: str, mask: List[bool]) -> bool:
    """``$$`` / ``$`` 的奇偶（状态机）校验：两者都应成对闭合。"""
    in_block = in_inline = False
    i, n = 0, len(src)
    while i < n:
        if mask[i]:
            i += 1
            continue
        if src[i:i + 2] == "$$":
            if not in_inline:            # $$ 在行内 $ 环境里不另算
                in_block = not in_block
            i += 2
            continue
        if src[i] == "$":
            if not in_block:
                in_inline = not in_inline
            i += 1
            continue
        i += 1
    return not in_block and not in_inline
