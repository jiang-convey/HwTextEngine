"""校验并修复作业答案文本。

    栈（:mod:`bracket_stack`）  —— 校验 () [] {} \\[\\] \\(\\) 与 $ / $$ 是否配对
    状态机（:mod:`delim_fix`）—— 把 \\[ \\] -> $$，\\( \\) -> $（代码块不动）
"""
from typing import Dict

from ..parsing.bracket_stack import check_brackets
from ..parsing.delim_fix import normalize_delims


def fix(src: str) -> Dict:
    """返回修复结果：修复前后配对报告、替换次数、修复后文本。"""
    before = check_brackets(src)
    fixed, replacements = normalize_delims(src)
    after = check_brackets(fixed)
    return {"fixed": fixed, "replacements": replacements,
            "before": before, "after": after}
