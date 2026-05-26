import uuid
import re

from sqlalchemy.orm import Session

from app.embeddings import embedding_provider
from app.models import Chunk, Document, Memory, Product


TOKEN_RE = re.compile(r"[\w\u4e00-\u9fff]+", re.UNICODE)


def split_text(content: str, max_chars: int = 700, overlap: int = 100) -> list[str]:
    content = " ".join(content.split())
    if not content:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(content):
        end = min(start + max_chars, len(content))
        chunks.append(content[start:end])
        if end == len(content):
            break
        start = max(end - overlap, start + 1)
    return chunks


def product_to_knowledge(product: Product, extra_text: str | None = None) -> str:
    parts = [
        f"产品名称：{product.name}",
        f"类目：{product.category or ''}",
        f"目标人群：{product.target_audience or ''}",
        f"卖点：{product.selling_points or ''}",
        f"注意事项：{product.cautions or ''}",
    ]
    if extra_text:
        parts.append(f"补充资料：{extra_text}")
    return "\n".join(parts)


def ingest_text(
    db: Session,
    *,
    title: str,
    content: str,
    source_type: str = "manual",
    product_id: uuid.UUID | None = None,
    metadata: dict | None = None,
) -> Document:
    document = Document(title=title, source_type=source_type, doc_metadata=metadata or {})
    db.add(document)
    db.flush()

    for index, chunk_text in enumerate(split_text(content)):
        db.add(
            Chunk(
                document_id=document.id,
                product_id=product_id,
                content=chunk_text,
                chunk_index=index,
                embedding=embedding_provider.embed(chunk_text),
                chunk_metadata=metadata or {},
            )
        )
    return document


def search_chunks(db: Session, query: str, limit: int = 5) -> list[dict]:
    query_embedding = embedding_provider.embed(query)
    rows = db.query(Chunk).all()
    documents = {
        document.id: document
        for document in db.query(Document).filter(Document.id.in_([row.document_id for row in rows])).all()
    } if rows else {}
    scored = []
    for row in rows:
        stored_embedding = normalize_embedding(row.embedding)
        vector_score = cosine_similarity(query_embedding, stored_embedding)
        keyword_score = keyword_overlap(query, row.content)
        score = (0.82 * vector_score) + (0.18 * keyword_score)
        document = documents.get(row.document_id)
        scored.append(
            {
                "content": row.content,
                "metadata": row.chunk_metadata,
                "score": score,
                "source": build_source_label(document, row),
            }
        )
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]


def keyword_overlap(query: str, content: str) -> float:
    query_terms = set(TOKEN_RE.findall(query.lower()))
    if not query_terms:
        return 0.0
    content_lower = content.lower()
    hits = sum(1 for term in query_terms if term and term in content_lower)
    return hits / len(query_terms)


def build_source_label(document: Document | None, chunk: Chunk) -> str:
    metadata = chunk.chunk_metadata or {}
    filename = metadata.get("filename")
    sheet = metadata.get("sheet")
    row = metadata.get("row")
    product_name = metadata.get("product_name")
    parts = []
    if filename:
        parts.append(str(filename))
    elif document:
        parts.append(document.title)
    if sheet:
        parts.append(str(sheet))
    if row:
        parts.append(f"第 {row} 行")
    if product_name:
        parts.append(str(product_name))
    return " / ".join(parts) if parts else "知识库片段"


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def normalize_embedding(value) -> list[float]:
    if value is None:
        return []
    try:
        return [float(item) for item in value.tolist()]
    except AttributeError:
        return [float(item) for item in value]


def recent_memories(db: Session, limit: int = 5) -> list[Memory]:
    return db.query(Memory).order_by(Memory.created_at.desc()).limit(limit).all()


def compose_answer(question: str, chunks: list[dict], memories: list[Memory]) -> str:
    if not chunks:
        return "我还没有检索到相关产品资料。你可以先添加产品，或上传产品文档后再问我。"

    memory_text = "\n".join(f"- {memory.content}" for memory in memories) or "暂无长期记忆。"
    context_text = "\n\n".join(f"[资料 {idx + 1}]\n{chunk['content']}" for idx, chunk in enumerate(chunks))
    return (
        "下面是基于当前产品资料库的回答。\n\n"
        f"你的问题：{question}\n\n"
        f"已参考的长期记忆：\n{memory_text}\n\n"
        f"相关资料：\n{context_text}\n\n"
        "初版 MVP 现在使用本地检索和模板化回答；接入大模型 API 后，这里会升级为更自然的策略分析、脚本创作和多步骤推理。"
    )
