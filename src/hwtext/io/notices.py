"""I/O 边界：读取公告文本（单文件或目录）。"""
import os
from typing import List, Tuple


def iter_notices(path: str) -> List[Tuple[str, str]]:
    """``path`` 是文件 -> ``[(文件名, 文本)]``；是目录 -> 读其中的 .txt / .md。"""
    out: List[Tuple[str, str]] = []
    if os.path.isdir(path):
        for name in sorted(os.listdir(path)):
            if name.lower().endswith((".txt", ".md")):
                full = os.path.join(path, name)
                with open(full, encoding="utf-8") as f:
                    out.append((name, f.read()))
    else:
        with open(path, encoding="utf-8") as f:
            out.append((os.path.basename(path), f.read()))
    return out
