"""按题号在教材纯文本里定位题目并切出题面。

串联两种自实现算法：
    KMP            —— 定位「习题 3.2」这类题号标记的位置
    编辑距离 DP    —— 精确题号找不到时，给出最接近的候选题号
"""
from typing import Dict, List

from ..matching.edit_distance import rank_candidates
from ..matching.kmp import find_all

_SPACES = " \t　"


def marker_variants(pid: str, scheme: str = "习题") -> List[str]:
    """生成题号标记的几种写法：``习题3.2`` / ``习题 3.2`` / ``习题　3.2``。"""
    pid = pid.strip()
    out, seen = [], set()
    for v in (scheme + pid, scheme + " " + pid, scheme + "　" + pid):
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _read_number_token(text: str, i: int) -> str:
    """从下标 ``i`` 起跳过空白后，读形如 ``3`` / ``3.2`` / ``3.2.1`` 的编号。"""
    j = i
    while j < len(text) and text[j] in _SPACES:
        j += 1
    start = j
    while j < len(text) and (text[j].isdigit() or text[j] in ".．"):
        j += 1
    return text[start:j].strip(".．")


def discover_ids(text: str, scheme: str = "习题") -> List[str]:
    """扫描出文本里所有 ``<scheme> 数字`` 的编号（用于给候选排序）。"""
    seen, out = set(), []
    for pos in find_all(text, scheme):
        tok = _read_number_token(text, pos + len(scheme))
        if tok and tok[0].isdigit() and tok not in seen:
            seen.add(tok)
            out.append(tok)
    return out


def locate_one(text: str, pid: str, scheme: str = "习题",
               window: int = 1200) -> Dict:
    """定位单个题号。找到则切出到下一个题号标记之间的题面；否则给候选。"""
    start, used = -1, None
    for v in marker_variants(pid, scheme):
        hits = find_all(text, v)
        if hits:
            start, used = hits[0], v
            break
    if start < 0:
        cands = [c for c, _ in rank_candidates(pid, discover_ids(text, scheme), 5)]
        return {"number": pid, "found": False, "candidates": cands}
    after = [p for p in find_all(text, scheme) if p > start]
    end = min(after) if after else min(len(text), start + window)
    return {"number": pid, "found": True, "marker": used,
            "char_start": start, "char_end": end,
            "content": text[start:end].strip()}


def locate(text: str, pids: List[str], scheme: str = "习题") -> Dict:
    """批量定位题号，返回结构化结果（兼容下游「整理进作业」流程）。"""
    problems = [locate_one(text, p, scheme) for p in pids]
    return {"scheme": scheme, "count": len(problems), "problems": problems,
            "missing": [p["number"] for p in problems if not p["found"]]}
