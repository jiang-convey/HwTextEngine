"""把 LaTeX 行间/行内分隔符规整为美元符号，避免在 Markdown + MathJax 里转录出错。

    \\[ ... \\]   ->   $$ ... $$          \\( ... \\)   ->   $ ... $

知识点
    有限状态机（复用 :mod:`tokenizer` 的代码保护掩码）。
约束
    代码块 / 行内代码内部**原样保留**——不能动用户贴进来的示例代码。
背景
    人/AI 写答案时常用 ``\\[ \\]`` ``\\( \\)``，但很多 Markdown 渲染器只认
    ``$$`` ``$``；不统一就会出现公式不渲染或整段串味。
"""
from typing import Tuple

from .tokenizer import protected_mask

# 两字符定界符 -> 目标
_REPLACE = {"\\[": "$$", "\\]": "$$", "\\(": "$", "\\)": "$"}


def normalize_delims(src: str) -> Tuple[str, int]:
    """返回 ``(修复后的文本, 替换次数)``；代码区域不动。"""
    mask = protected_mask(src)
    out = []
    i, n, count = 0, len(src), 0
    while i < n:
        two = src[i:i + 2]
        # 两个字符都不在代码内，才替换
        if two in _REPLACE and not mask[i] and (i + 1 >= n or not mask[i + 1]):
            out.append(_REPLACE[two])
            count += 1
            i += 2
            continue
        out.append(src[i])
        i += 1
    return "".join(out), count
