"""源码扫描：用**有限状态机**标记哪些字符位于「代码」内。

知识点
    有限状态机（三态：NORMAL / INLINE / FENCED）。
作用
    公式分隔符修复（:mod:`delim_fix`）与括号配对（:mod:`bracket_stack`）都必须
    「跳过代码块」——否则会把用户贴的示例代码里的 ``\\(``、``[`` 也当成数学
    定界符乱改。本模块提供统一的 :func:`protected_mask`，避免各模块各写一套
    扫描逻辑、各错一次。

状态转移
    NORMAL --行首```--> FENCED --行首```--> NORMAL
    NORMAL --`-------> INLINE --`/换行----> NORMAL
"""
from typing import List, Tuple

FENCE = "```"


def protected_mask(src: str) -> List[bool]:
    """返回与 ``src`` 等长的布尔表：``True`` 表示该字符位于代码内，应被保护。"""
    n = len(src)
    mask = [False] * n
    state = "NORMAL"                      # NORMAL | INLINE | FENCED
    i = 0
    while i < n:
        line_start = (i == 0 or src[i - 1] == "\n")
        # 行首的 ``` 切换围栏代码块状态（开/关都把这三个反引号算作代码）
        if line_start and src.startswith(FENCE, i):
            for j in range(i, min(i + 3, n)):
                mask[j] = True
            state = "NORMAL" if state == "FENCED" else "FENCED"
            i += 3
            continue
        ch = src[i]
        if state == "FENCED":
            mask[i] = True
            i += 1
            continue
        if ch == "\n":
            if state == "INLINE":
                state = "NORMAL"          # 行内代码不跨行
            i += 1
            continue
        if ch == "`":
            mask[i] = True                # 反引号本身也算代码边界
            state = "NORMAL" if state == "INLINE" else "INLINE"
            i += 1
            continue
        if state == "INLINE":
            mask[i] = True
        i += 1
    return mask


def segments(src: str) -> List[Tuple[bool, str]]:
    """把 ``src`` 切成 ``(is_protected, text)`` 连续段，便于按段处理。"""
    mask = protected_mask(src)
    out: List[Tuple[bool, str]] = []
    if not src:
        return out
    start = 0
    cur = mask[0]
    for i in range(1, len(src)):
        if mask[i] != cur:
            out.append((cur, src[start:i]))
            start, cur = i, mask[i]
    out.append((cur, src[start:]))
    return out
