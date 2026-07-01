"""Word(.docx)→ Markdown 解析器

保留标题层级、列表、加粗、表格，供文档上传 / 文件更新 / 初始导入复用。
"""
import re
from typing import Union
from io import BytesIO

from docx import Document as DocxDoc
from docx.table import Table
from docx.text.paragraph import Paragraph


def _runs_to_markdown(para: Paragraph) -> str:
    """拼接段落内的 run，保留加粗格式"""
    parts = []
    for run in para.runs:
        t = run.text
        if not t:
            continue
        if run.bold:
            # 仅在非空白片段两侧加 **，避免 ** ** 这种无效语法
            stripped = t.strip()
            if stripped:
                lead = t[: len(t) - len(t.lstrip())]
                trail = t[len(t.rstrip()):]
                t = f"{lead}**{stripped}**{trail}"
        parts.append(t)
    joined = "".join(parts).strip()
    return joined or para.text.strip()


def _para_to_markdown(para: Paragraph) -> str:
    """单个段落 → Markdown 行（识别标题层级、列表、加粗）"""
    text = para.text.strip()
    if not text:
        return ""

    style = (para.style.name or "").lower()

    # 标题：Word 样式名形如 "Heading 1" / "标题 1"
    m = re.search(r"(?:heading|标题)\s*(\d+)", style)
    if m:
        level = min(int(m.group(1)), 6)
        return f"{'#' * level} {text}"

    # 列表：Word 样式名含 list/列表
    if "list" in style or "列表" in style:
        ordered = "number" in style or "编号" in style
        prefix = "1." if ordered else "-"
        return f"{prefix} {_runs_to_markdown(para)}"

    return _runs_to_markdown(para)


def _table_to_markdown(table: Table) -> str:
    """Word 表格 → Markdown 表格"""
    rows = []
    for row in table.rows:
        cells = [c.text.strip().replace("\n", " ").replace("|", "\\|") for c in row.cells]
        rows.append(cells)
    if not rows:
        return ""

    col_count = max(len(r) for r in rows)
    rows = [r + [""] * (col_count - len(r)) for r in rows]

    lines = ["| " + " | ".join(rows[0]) + " |"]
    lines.append("| " + " | ".join(["---"] * col_count) + " |")
    for r in rows[1:]:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def parse_docx_to_markdown(source: Union[str, bytes, BytesIO]) -> str:
    """解析 .docx 为 Markdown（保留标题层级、列表、加粗、表格）

    source 可为文件路径、bytes 或 BytesIO。
    """
    if isinstance(source, bytes):
        source = BytesIO(source)
    doc = DocxDoc(source)

    # 按文档顺序遍历 body，使表格与段落保持原始位置
    blocks = []
    for child in doc.element.body.iterchildren():
        if child.tag.endswith("}p"):
            md = _para_to_markdown(Paragraph(child, doc))
            if md:
                blocks.append(md)
        elif child.tag.endswith("}tbl"):
            md = _table_to_markdown(Table(child, doc))
            if md:
                blocks.append(md)

    return "\n\n".join(blocks)
