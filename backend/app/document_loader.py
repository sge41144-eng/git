from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd


SUPPORTED_SUFFIXES = {".txt", ".md", ".csv", ".xlsx", ".xls", ".pdf"}


def read_text_file(path: Path) -> str:
    raw = path.read_bytes()
    return read_text_bytes(raw)


def read_text_bytes(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def read_spreadsheet_bytes(raw: bytes, filename: str) -> list[tuple[str, str, dict]]:
    documents: list[tuple[str, str, dict]] = []
    sheets = pd.read_excel(BytesIO(raw), sheet_name=None, dtype=str, header=None).items()
    for sheet_name, frame in sheets:
        lines = []
        for row_index, row in frame.iterrows():
            values = [normalize_cell(value) for value in row.tolist()]
            values = [value for value in values if value]
            if values:
                lines.append(f"第{row_index + 1}行：" + " | ".join(values))
        if lines:
            title = f"{filename} / {sheet_name}"
            documents.append(
                (
                    title,
                    "\n".join(lines),
                    {"filename": filename, "sheet": sheet_name},
                )
            )
    return documents


def read_pdf_bytes(raw: bytes, filename: str) -> list[tuple[str, str, dict]]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("当前环境还没有安装 pypdf，无法解析 PDF。请先执行：pip install pypdf") from exc

    reader = PdfReader(BytesIO(raw))
    documents: list[tuple[str, str, dict]] = []
    for page_index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            documents.append(
                (
                    f"{filename} / 第{page_index + 1}页",
                    text,
                    {"filename": filename, "page": page_index + 1},
                )
            )
    return documents


def parse_file_bytes(filename: str, raw: bytes) -> list[tuple[str, str, dict]]:
    suffix = Path(filename).suffix.lower()
    if suffix in {".txt", ".md", ".csv"}:
        return [(filename, read_text_bytes(raw), {"filename": filename})]
    if suffix in {".xlsx", ".xls"}:
        return read_spreadsheet_bytes(raw, filename)
    if suffix == ".pdf":
        return read_pdf_bytes(raw, filename)
    raise ValueError(f"暂不支持的文件类型：{suffix or '无后缀'}")


def parse_file_path(path: Path) -> list[tuple[str, str, dict]]:
    return parse_file_bytes(path.name, path.read_bytes())


def iter_supported_files(directory: Path) -> list[Path]:
    return [
        path
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    ]


def normalize_cell(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()
