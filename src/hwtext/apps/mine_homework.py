"""从公告正文里挖出「隐藏作业」。

核心是 **Aho-Corasick**：把一大批作业信号关键词编进一台自动机，对公告正文
**一遍扫描**同时命中全部关键词；再用 KMP 抽取题号 / 截止线索。
"""
from typing import Dict, List, Optional, Tuple

from ..matching.aho_corasick import AhoCorasick
from ..matching.kmp import find_all

# 作业信号关键词（多模式串）
KEYWORDS = [
    "作业", "习题", "练习", "题目", "课后", "上交", "提交", "截止", "ddl",
    "deadline", "due", "第", "页", "homework", "assignment", "exercise", "hw",
]
# 强信号：出现即基本可判定为作业
STRONG = {"作业", "上交", "提交", "截止", "ddl", "deadline", "due",
          "homework", "assignment"}
_DUE_MARKERS = ["截止", "deadline", "ddl", "due"]
_SPACES = " \t　"


def _num_after(text: str, i: int):
    """从 ``i`` 起跳过空白后读编号，返回 ``(编号, 编号结束的下标)``。"""
    j = i
    while j < len(text) and text[j] in _SPACES:
        j += 1
    start = j
    # 数字、小数点、区间号（-~～）算作编号；中文顿号、逗号视为分隔，不并入
    while j < len(text) and (text[j].isdigit() or text[j] in ".．-~～"):
        j += 1
    return text[start:j].strip(".．-~～"), j


def _problem_refs(text: str) -> List[str]:
    seen, out = set(), []
    # 习题 / 练习 / Exercise / Problem：前缀 + 编号
    for mk in ("习题", "练习", "exercise", "problem"):
        for pos in find_all(text, mk):
            tok, _ = _num_after(text, pos + len(mk))
            if tok and tok[0].isdigit():
                ref = mk + tok
                if ref not in seen:
                    seen.add(ref)
                    out.append(ref)
    # 「第 N 题」：要求编号后跟「题」，以排除「第6周」「第三节课」这类非题号
    for pos in find_all(text, "第"):
        tok, j = _num_after(text, pos + len("第"))
        while j < len(text) and text[j] in _SPACES:
            j += 1
        if tok and tok[0].isdigit() and j < len(text) and text[j] == "题":
            ref = "第" + tok + "题"
            if ref not in seen:
                seen.add(ref)
                out.append(ref)
    return out


def _due(text: str) -> Optional[str]:
    for mk in _DUE_MARKERS:
        hits = find_all(text, mk)
        if hits:
            return text[hits[0]: hits[0] + 40].replace("\n", " ").strip()
    return None


def mine(text: str, source: str = "") -> Optional[Dict]:
    """扫描单条公告，返回作业候选；完全没有关键词则返回 ``None``。"""
    hits = AhoCorasick(KEYWORDS).search(text)
    if not hits:
        return None
    tally: Dict[str, int] = {}
    for h in hits:
        tally[h.pattern] = tally.get(h.pattern, 0) + 1
    strong = sorted(k for k in tally if k in STRONG)
    refs = _problem_refs(text)
    due = _due(text)
    anchor = next((h for h in hits if h.pattern in STRONG), hits[0])
    s, e = max(0, anchor.start - 30), min(len(text), anchor.end + 70)
    # 判定为作业：有明确题号；或有强信号词且同时给出了截止线索。
    # （只出现「作业」二字而无题号/截止——如「本通知不涉及作业」——不算。）
    is_homework = bool(refs) or (bool(strong) and due is not None)
    return {
        "source": source,
        "is_homework": is_homework,
        "keywords": tally,
        "strong": strong,
        "problem_refs": refs,
        "due": due,
        "snippet": text[s:e].replace("\n", " ").strip(),
    }


def mine_all(notices: List[Tuple[str, str]]) -> List[Dict]:
    """对多条 ``(名称, 文本)`` 公告挖作业，只保留判定为作业的候选。"""
    out = []
    for name, text in notices:
        c = mine(text, source=name)
        if c and c["is_homework"]:
            out.append(c)
    return out
