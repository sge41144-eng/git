from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.config import settings
from app.db import SessionLocal
from app.rag import ingest_text


def read_txt(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


FORBIDDEN_COLUMN_KEYWORDS = ("禁忌", "禁止", "禁用", "不能说", "不可说")
RECOMMENDED_COLUMN_KEYWORDS = ("替换", "可用话术", "回复客户版")
FACT_COLUMN_KEYWORDS = ("用法用量", "注意事项", "适用人群", "配料", "核心成分", "核心卖点", "主要功效")


def read_xlsx(path: Path) -> list[tuple[str, str, dict]]:
    documents: list[tuple[str, str, dict]] = []
    sheets = pd.read_excel(path, sheet_name=None, dtype=str, header=None).items()
    for sheet_name, raw_frame in sheets:
        header_index = detect_header_row(raw_frame)
        if header_index is None:
            continue
        columns = [normalize_cell(value) or f"未命名列{index + 1}" for index, value in raw_frame.iloc[header_index].items()]
        frame = raw_frame.iloc[header_index + 1 :].copy()
        frame.columns = columns
        frame = frame.dropna(how="all").fillna("")
        if frame.empty:
            continue
        for row_index, row in frame.iterrows():
            fields = [
                "下面是一条产品资料记录。请严格区分事实信息、推荐话术和禁用表达。",
                "禁用表达只代表销售/客服不能这样说，不能当作产品事实或适用限制。",
            ]
            product_name = normalize_cell(row.get("产品名", "")) or normalize_cell(row.get("产品名称", ""))
            for column, value in row.items():
                value_text = normalize_cell(value)
                if value_text:
                    fields.append(format_xlsx_field(str(column), value_text))
            if fields:
                title = f"{path.name} / {sheet_name} / {product_name or f'第{row_index + 1}行'}"
                documents.append(
                    (
                        title,
                        "\n".join(fields),
                        {
                            "filename": path.name,
                            "sheet": sheet_name,
                            "row": int(row_index + 1),
                            "product_name": product_name,
                        },
                    )
                )
    return documents


def detect_header_row(frame: pd.DataFrame) -> int | None:
    for index, row in frame.iterrows():
        values = {normalize_cell(value) for value in row.tolist()}
        if "产品名" in values and "用法用量" in values:
            return int(index)
    return None


def normalize_cell(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def format_xlsx_field(column: str, value: str) -> str:
    if any(keyword in column for keyword in FORBIDDEN_COLUMN_KEYWORDS):
        return f"禁用表达（禁止这样对客户说，不代表事实结论）：{value}"
    if any(keyword in column for keyword in RECOMMENDED_COLUMN_KEYWORDS):
        return f"推荐话术/可用表达：{value}"
    if any(keyword in column for keyword in FACT_COLUMN_KEYWORDS):
        return f"事实资料 - {column}：{value}"
    return f"{column}：{value}"


def reset_database() -> None:
    with SessionLocal() as db:
        db.execute(text("TRUNCATE TABLE chunks, documents, products, memories CASCADE"))
        db.execute(text(f"ALTER TABLE chunks ALTER COLUMN embedding TYPE vector({settings.embedding_dimension})"))
        db.commit()


def ingest_directory(directory: Path) -> dict:
    ingested = []
    with SessionLocal() as db:
        for path in sorted(directory.iterdir()):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            if suffix == ".txt":
                content = read_txt(path)
                doc = ingest_text(
                    db,
                    title=path.name,
                    content=content,
                    source_type="file",
                    metadata={"filename": path.name},
                )
                ingested.append({"file": path.name, "document_id": str(doc.id), "type": "txt"})
            elif suffix == ".xlsx":
                for title, content, metadata in read_xlsx(path):
                    doc = ingest_text(
                        db,
                        title=title,
                        content=content,
                        source_type="xlsx",
                        metadata=metadata,
                    )
                    ingested.append({"file": title, "document_id": str(doc.id), "type": "xlsx"})
        db.commit()
    return {"ingested": ingested, "count": len(ingested)}


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m app.ingest_files <directory> [--reset]")
    directory = Path(sys.argv[1])
    if "--reset" in sys.argv:
        reset_database()
    result = ingest_directory(directory)
    print(result)


if __name__ == "__main__":
    main()
