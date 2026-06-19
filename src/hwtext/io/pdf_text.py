"""I/O 边界：把 PDF 解码成纯文本（pymupdf 优先，pdfplumber 兜底）。

这里**只**调用第三方库做解码；返回的字符串之后全部交给自实现算法处理。
缺库时给出明确的安装提示，而不是静默失败。
"""
from typing import List, Optional


def extract_pages(path: str) -> List[str]:
    """逐页返回 PDF 文本。"""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        fitz = None
    if fitz is not None:
        doc = fitz.open(path)
        try:
            return [page.get_text() for page in doc]
        finally:
            doc.close()
    try:
        import pdfplumber
    except ImportError:
        raise SystemExit(
            "读取 PDF 需要 pymupdf 或 pdfplumber：pip install pymupdf "
            "（或 pip install -r requirements.txt）")
    out: List[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            out.append(page.extract_text() or "")
    return out


def extract_text(path: str, pages: Optional[List[int]] = None) -> str:
    """返回整本 PDF 文本；``pages`` 给定时只取这些页（0 基下标）。"""
    all_pages = extract_pages(path)
    if pages:
        all_pages = [all_pages[i] for i in pages if 0 <= i < len(all_pages)]
    return "\n".join(all_pages)


def load_document(path: str, pages: Optional[List[int]] = None) -> str:
    """按扩展名加载文本：``.pdf`` 走解码，``.txt/.md`` 等直接读。"""
    if path.lower().endswith(".pdf"):
        return extract_text(path, pages=pages)
    with open(path, encoding="utf-8") as f:
        return f.read()
