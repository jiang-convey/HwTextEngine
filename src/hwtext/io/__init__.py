"""I/O 边界子包。

**整个项目唯一允许调用第三方库的地方**，且只做「解码 / 读文件」——拿到字符串
之后，所有检索 / 匹配 / 解析 / 压缩都交给自实现算法。把库隔离在这一层，是为了
让「算法内核零依赖」这一点可被清晰核查（见 README 学术诚信声明）。
"""
from .pdf_text import extract_pages, extract_text, load_document
from .notices import iter_notices

__all__ = ["extract_pages", "extract_text", "load_document", "iter_notices"]
