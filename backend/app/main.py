from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base, engine, get_db
from app.document_loader import iter_supported_files, parse_file_bytes, parse_file_path
from app.models import Chunk, Document, GenerationHistory, Memory, Product, ViralCase
from app.llm import generate_answer, summarize_conversation_memory, summarize_session_context
from app.rag import (
    compose_answer,
    get_session_summary,
    ingest_text,
    memory_context_for_chat,
    product_to_knowledge,
    recent_memories,
    search_chunks,
    split_text,
)
from app.schemas import (
    ChatRequest,
    ChatResponse,
    FolderAnalyzeRequest,
    FolderIngestRequest,
    FolderIngestResponse,
    GenerationHistoryOut,
    HistoryToCaseRequest,
    MemoryCreate,
    ProductCreate,
    ProductOut,
    SearchResult,
    ViralCaseCreate,
    ViralCaseOut,
)
from app.ui import HOME_HTML
from app.workflows import (
    ContentCreateRequest,
    ContentCreateResponse,
    create_content_plan,
)
from app.web_search import multi_search, web_search_with_diagnostics


app = FastAPI(title="Product Operations Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def ensure_tables() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return HOME_HTML
    return """
    <!doctype html>
    <html lang="zh-CN">
      <head>
        <meta charset="utf-8" />
        <title>产品运营智能体 MVP</title>
        <style>
          * { box-sizing: border-box; }
          body {
            font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
            margin: 0;
            color: #202124;
            background: #f7f8fa;
          }
          header {
            padding: 24px 32px;
            background: #ffffff;
            border-bottom: 1px solid #e7e9ee;
          }
          h1 { margin: 0 0 8px; font-size: 28px; }
          p { margin: 0; color: #5f6673; }
          main {
            display: grid;
            grid-template-columns: minmax(320px, 420px) 1fr;
            gap: 20px;
            padding: 24px 32px;
          }
          section {
            background: #ffffff;
            border: 1px solid #e7e9ee;
            border-radius: 8px;
            padding: 18px;
          }
          h2 { margin: 0 0 14px; font-size: 18px; }
          label {
            display: block;
            margin-top: 12px;
            font-size: 13px;
            color: #4b5563;
          }
          textarea, input {
            width: 100%;
            padding: 10px 12px;
            margin-top: 6px;
            border: 1px solid #ccd1d9;
            border-radius: 6px;
            font: inherit;
            background: #ffffff;
          }
          textarea { resize: vertical; }
          button {
            margin-top: 14px;
            padding: 10px 16px;
            border: 0;
            border-radius: 6px;
            background: #1769e0;
            color: #ffffff;
            font: inherit;
            cursor: pointer;
          }
          button.secondary { background: #475569; }
          .output {
            min-height: 260px;
            background: #ffffff;
            border: 1px solid #e7e9ee;
            padding: 16px;
            border-radius: 8px;
            overflow: auto;
          }
          .answer {
            white-space: pre-wrap;
            line-height: 1.7;
            margin-bottom: 16px;
          }
          .result-item {
            padding: 12px;
            border: 1px solid #e7e9ee;
            border-radius: 6px;
            margin-top: 10px;
            background: #f8fafc;
          }
          .result-item strong { display: block; margin-bottom: 6px; }
          .muted { color: #64748b; font-size: 13px; }
          .error { color: #b42318; white-space: pre-wrap; }
          .stack { display: grid; gap: 20px; }
          .hint { margin-top: 10px; font-size: 13px; color: #6b7280; }
          @media (max-width: 900px) {
            main { grid-template-columns: 1fr; padding: 16px; }
            header { padding: 20px 16px; }
          }
        </style>
      </head>
      <body>
        <header>
          <h1>产品运营智能体 MVP</h1>
          <p>当前版本用于验证产品资料入库、长期记忆和基础 RAG 检索。接口文档：<a href="/docs">/docs</a></p>
        </header>
        <main>
          <div class="stack">
            <section>
              <h2>添加产品资料</h2>
              <label>产品名称<input id="productName" placeholder="例如：520香氛礼盒"></label>
              <label>产品类目<input id="category" placeholder="例如：节日礼盒"></label>
              <label>目标人群<input id="audience" placeholder="例如：20-35岁女性、情侣送礼人群"></label>
              <label>核心卖点<textarea id="sellingPoints" rows="3" placeholder="例如：高颜值包装、淡雅花果香、适合520送礼"></textarea></label>
              <label>宣传注意事项<textarea id="cautions" rows="2" placeholder="例如：不承诺治疗、改善睡眠等功效；避免绝对化宣传"></textarea></label>
              <label>补充知识<textarea id="knowledgeText" rows="4" placeholder="例如：适合抖音短视频场景、内容钩子、活动玩法、FAQ等"></textarea></label>
              <button onclick="createProduct()">保存产品并入库</button>
              <div class="hint">保存后会自动切片并写入向量库。</div>
            </section>
            <section>
              <h2>保存长期记忆</h2>
              <label>记忆内容<textarea id="memoryContent" rows="3" placeholder="例如：以后给我活动方案时，先给结论，再给执行清单。"></textarea></label>
              <button class="secondary" onclick="saveMemory()">保存记忆</button>
            </section>
          </div>
          <section>
            <h2>对话测试</h2>
            <label>问题<textarea id="q" rows="5" placeholder="例如：帮我给520香氛礼盒做一个抖音短视频脚本方向"></textarea></label>
            <button onclick="ask()">发送问题</button>
            <button class="secondary" onclick="loadCounts()">查看数据量</button>
            <div class="output" id="out">等待操作...</div>
          </section>
        </main>
        <script>
          function show(data) {
            document.getElementById('out').textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
          }

          function escapeHtml(value) {
            return String(value ?? '')
              .replaceAll('&', '&amp;')
              .replaceAll('<', '&lt;')
              .replaceAll('>', '&gt;')
              .replaceAll('"', '&quot;')
              .replaceAll("'", '&#039;');
          }

          function showChat(data) {
            const retrieved = data.retrieved || [];
            const memories = data.memories || [];
            const html = `
              <div class="answer">${escapeHtml(data.answer || '')}</div>
              <h3>参考资料</h3>
              ${retrieved.length ? retrieved.map((item, index) => `
                <div class="result-item">
                  <strong>资料 ${index + 1} <span class="muted">相关度：${Number(item.score || 0).toFixed(3)}</span></strong>
                  <div>${escapeHtml(item.content)}</div>
                </div>
              `).join('') : '<div class="muted">没有检索到参考资料。</div>'}
              <h3>已读取的长期记忆</h3>
              ${memories.length ? memories.map((item) => `<div class="result-item">${escapeHtml(item)}</div>`).join('') : '<div class="muted">暂无长期记忆。</div>'}
            `;
            document.getElementById('out').innerHTML = html;
          }

          function showError(err) {
            document.getElementById('out').innerHTML = `<div class="error">操作失败：${escapeHtml(JSON.stringify(err, null, 2))}</div>`;
          }

          async function requestJson(url, body) {
            const res = await fetch(url, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(body)
            });
            const data = await res.json();
            if (!res.ok) throw data;
            return data;
          }

          async function createProduct() {
            try {
              const data = await requestJson('/products', {
                name: document.getElementById('productName').value,
                category: document.getElementById('category').value,
                target_audience: document.getElementById('audience').value,
                selling_points: document.getElementById('sellingPoints').value,
                cautions: document.getElementById('cautions').value,
                knowledge_text: document.getElementById('knowledgeText').value
              });
              show(`产品已保存并入库：${data.name}`);
            } catch (err) {
              showError(err);
            }
          }

          async function saveMemory() {
            try {
              const data = await requestJson('/memories', {
                memory_type: 'user_preference',
                content: document.getElementById('memoryContent').value,
                importance: 4
              });
              show('长期记忆已保存。');
            } catch (err) {
              showError(err);
            }
          }

          async function ask() {
            try {
              const data = await requestJson('/chat', {
                message: document.getElementById('q').value,
                session_id: 'browser'
              });
              showChat(data);
            } catch (err) {
              showError(err);
            }
          }

          async function loadCounts() {
            const res = await fetch('/debug/counts');
            show(await res.json());
          }
        </script>
      </body>
    </html>
    """


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.get("/debug/counts")
def debug_counts(db: Session = Depends(get_db)) -> dict:
    return {
        "products": db.query(Product).count(),
        "documents": db.query(Document).count(),
        "chunks": db.query(Chunk).count(),
        "memories": db.query(Memory).count(),
        "viral_cases": db.query(ViralCase).count(),
        "generation_history": db.query(GenerationHistory).count(),
    }


@app.get("/debug/chunks")
def debug_chunks(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.query(Chunk).order_by(Chunk.created_at.desc()).limit(10).all()
    return [
        {
            "id": str(row.id),
            "content": row.content,
            "metadata": row.chunk_metadata,
            "embedding_length": len(row.embedding) if row.embedding is not None else 0,
        }
        for row in rows
    ]


@app.get("/debug/search")
def debug_search(q: str = "抖音 牛初乳 爆款") -> dict:
    results, detail = web_search_with_diagnostics(q, limit=5)
    return {"query": q, "count": len(results), "diagnostics": detail, "results": results}


@app.post("/admin/rebuild-schema")
def rebuild_schema(db: Session = Depends(get_db)) -> dict:
    db.execute(text("TRUNCATE TABLE chunks, documents, products, memories CASCADE"))
    db.execute(
        text(
            f"ALTER TABLE chunks ALTER COLUMN embedding TYPE vector({settings.embedding_dimension})"
        )
    )
    db.commit()
    return {"reset": True, "embedding_dimension": settings.embedding_dimension}


@app.post("/products", response_model=ProductOut)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> Product:
    product = Product(
        name=payload.name,
        category=payload.category,
        target_audience=payload.target_audience,
        selling_points=payload.selling_points,
        cautions=payload.cautions,
    )
    db.add(product)
    db.flush()
    ingest_text(
        db,
        title=f"产品资料：{product.name}",
        content=product_to_knowledge(product, payload.knowledge_text),
        source_type="product",
        product_id=product.id,
        metadata={"product_name": product.name},
    )
    db.commit()
    db.refresh(product)
    return product


@app.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)) -> list[Product]:
    return db.query(Product).order_by(Product.created_at.desc()).all()


@app.post("/memories")
def create_memory(payload: MemoryCreate, db: Session = Depends(get_db)) -> dict:
    memory = Memory(
        memory_type=payload.memory_type,
        content=payload.content,
        importance=payload.importance,
    )
    db.add(memory)
    db.commit()
    return {"id": str(memory.id), "saved": True}


@app.post("/viral-cases", response_model=ViralCaseOut)
def create_viral_case(payload: ViralCaseCreate, db: Session = Depends(get_db)) -> ViralCase:
    analysis_question = (
        "请拆解这个短视频/竞品爆款案例，输出：开头钩子、目标人群、痛点、情绪价值、卖点植入、"
        "转化动作、可复用结构、合规风险。"
        f"\n\n平台：{payload.platform or ''}\n产品：{payload.product or ''}\n标题：{payload.title or ''}"
        f"\n链接：{payload.url or ''}\n作者：{payload.author or ''}\n数据：{payload.metrics}\n内容：{payload.content}"
    )
    analysis = generate_answer(analysis_question, [], recent_memories(db), mode="script") or ""
    viral_case = ViralCase(
        platform=payload.platform,
        product=payload.product,
        title=payload.title,
        url=payload.url,
        author=payload.author,
        content=payload.content,
        metrics=payload.metrics,
        analysis=analysis,
        tags=payload.tags,
    )
    db.add(viral_case)
    db.flush()
    knowledge = (
        f"爆款/竞品案例\n平台：{payload.platform or ''}\n产品：{payload.product or ''}\n"
        f"标题：{payload.title or ''}\n链接：{payload.url or ''}\n作者：{payload.author or ''}\n"
        f"数据：{payload.metrics}\n标签：{payload.tags or ''}\n内容：{payload.content}\n拆解：{analysis}"
    )
    ingest_text(
        db,
        title=f"爆款案例：{payload.title or payload.product or payload.platform or '未命名'}",
        content=knowledge,
        source_type="viral_case",
        metadata={"viral_case_id": str(viral_case.id), "platform": payload.platform, "product": payload.product},
    )
    db.commit()
    db.refresh(viral_case)
    return viral_case


@app.get("/viral-cases", response_model=list[ViralCaseOut])
def list_viral_cases(db: Session = Depends(get_db)) -> list[ViralCase]:
    return db.query(ViralCase).order_by(ViralCase.created_at.desc()).limit(50).all()


def build_history_title(history: GenerationHistory) -> str:
    parts = [history.platform, history.product, history.goal or history.content_module]
    title = " ".join(part for part in parts if part)
    return title or "生成内容案例"


def save_generation_history(
    db: Session,
    *,
    workflow: str,
    platform: str | None,
    product: str | None,
    content_module: str | None,
    goal: str | None,
    audience: str | None,
    keywords: str | None,
    input_payload: dict,
    output_content: str,
    source_summary: dict,
) -> GenerationHistory:
    history = GenerationHistory(
        workflow=workflow,
        platform=platform,
        product=product,
        content_module=content_module,
        goal=goal,
        audience=audience,
        keywords=keywords,
        input_payload=input_payload,
        output_content=output_content,
        source_summary=source_summary,
        status="draft",
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


@app.get("/generation-history", response_model=list[GenerationHistoryOut])
def list_generation_history(db: Session = Depends(get_db)) -> list[GenerationHistory]:
    return db.query(GenerationHistory).order_by(GenerationHistory.created_at.desc()).limit(80).all()


@app.delete("/generation-history/{history_id}")
def delete_generation_history(history_id: str, db: Session = Depends(get_db)) -> dict:
    history = db.get(GenerationHistory, history_id)
    if not history:
        raise HTTPException(status_code=404, detail="生成历史不存在")
    db.delete(history)
    db.commit()
    return {"deleted": True, "id": history_id}


@app.post("/generation-history/{history_id}/to-case", response_model=ViralCaseOut)
def convert_history_to_case(history_id: str, payload: HistoryToCaseRequest, db: Session = Depends(get_db)) -> ViralCase:
    history = db.get(GenerationHistory, history_id)
    if not history:
        raise HTTPException(status_code=404, detail="生成历史不存在")

    content_parts = [history.output_content]
    if payload.notes:
        content_parts.append(f"\n发布复盘/补充说明：{payload.notes}")
    source_summary = history.source_summary or {}
    if source_summary:
        content_parts.append(f"\n生成时参考来源：{source_summary}")

    case_payload = ViralCaseCreate(
        platform=history.platform,
        product=history.product,
        title=payload.title or build_history_title(history),
        url=payload.url,
        author=payload.author,
        content="\n\n".join(content_parts),
        metrics=payload.metrics,
        tags=payload.tags or history.content_module or history.workflow,
    )
    viral_case = create_viral_case(case_payload, db)
    history.status = "converted"
    history.converted_case_id = viral_case.id
    db.commit()
    db.refresh(viral_case)
    return viral_case


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    raw = await file.read()
    try:
        parsed_documents = parse_file_bytes(file.filename or "uploaded-document", raw)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    saved = []
    for title, content, metadata in parsed_documents:
        document = ingest_text(
            db,
            title=title,
            content=content,
            source_type="upload",
            metadata=metadata,
        )
        saved.append({"document_id": str(document.id), "title": title, "chunks": len(split_text(content))})
    db.commit()
    return {"filename": file.filename, "saved": True, "count": len(saved), "documents": saved}


@app.post("/documents/analyze-upload")
async def analyze_uploaded_document(
    file: UploadFile = File(...),
    instruction: str = Form("请分析这个文件的核心内容、可用于产品运营的要点和需要注意的风险。"),
    db: Session = Depends(get_db),
) -> dict:
    raw = await file.read()
    try:
        parsed_documents = parse_file_bytes(file.filename or "uploaded-document", raw)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    chunks = []
    for index, (title, content, metadata) in enumerate(parsed_documents[:8]):
        preview = content[:2200]
        chunks.append(
            {
                "content": preview,
                "score": 1.0 - (index * 0.01),
                "metadata": metadata,
                "source": title,
            }
        )
    memories = recent_memories(db)
    question = f"{instruction}\n\n文件名：{file.filename}"
    answer = generate_answer(question, chunks, memories, mode="qa") or compose_answer(question, chunks, memories)
    return {"filename": file.filename, "answer": answer, "preview_documents": chunks}


@app.post("/documents/ingest-folder", response_model=FolderIngestResponse)
def ingest_folder(payload: FolderIngestRequest, db: Session = Depends(get_db)) -> FolderIngestResponse:
    folder = Path(payload.folder_path)
    if not folder.exists() or not folder.is_dir():
        raise HTTPException(status_code=400, detail=f"文件夹不存在：{payload.folder_path}")

    if payload.reset:
        db.execute(text("TRUNCATE TABLE chunks, documents, products, memories CASCADE"))
        db.execute(text(f"ALTER TABLE chunks ALTER COLUMN embedding TYPE vector({settings.embedding_dimension})"))
        db.flush()

    saved = []
    for path in iter_supported_files(folder):
        try:
            parsed_documents = parse_file_path(path)
        except (ValueError, RuntimeError) as exc:
            saved.append({"file": str(path), "saved": False, "error": str(exc)})
            continue
        for title, content, metadata in parsed_documents:
            metadata = {**metadata, "path": str(path)}
            document = ingest_text(
                db,
                title=title,
                content=content,
                source_type=path.suffix.lower().lstrip(".") or "file",
                metadata=metadata,
            )
            saved.append({"file": str(path), "title": title, "document_id": str(document.id), "saved": True})
    db.commit()
    return FolderIngestResponse(saved=True, count=sum(1 for item in saved if item.get("saved")), files=saved)


@app.post("/documents/analyze-folder")
def analyze_folder(payload: FolderAnalyzeRequest, db: Session = Depends(get_db)) -> dict:
    folder = Path(payload.folder_path)
    if not folder.exists() or not folder.is_dir():
        raise HTTPException(status_code=400, detail=f"文件夹不存在：{payload.folder_path}")

    chunks = []
    errors = []
    for path in iter_supported_files(folder):
        if len(chunks) >= payload.max_documents:
            break
        try:
            parsed_documents = parse_file_path(path)
        except (ValueError, RuntimeError) as exc:
            errors.append({"file": str(path), "error": str(exc)})
            continue
        for title, content, metadata in parsed_documents:
            if len(chunks) >= payload.max_documents:
                break
            chunks.append(
                {
                    "content": content[:2200],
                    "score": 1.0,
                    "metadata": {**metadata, "path": str(path)},
                    "source": title,
                }
            )

    if not chunks:
        raise HTTPException(status_code=400, detail="没有找到可分析的 txt、md、csv、xlsx、xls 或 pdf 文件。")

    memories = recent_memories(db)
    question = f"{payload.instruction}\n\n文件夹：{payload.folder_path}"
    answer = generate_answer(question, chunks, memories, mode="qa") or compose_answer(question, chunks, memories)
    return {"folder_path": payload.folder_path, "answer": answer, "preview_documents": chunks, "errors": errors}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    history = [item.model_dump() for item in payload.history][-24:]
    source_mode = normalize_source_mode(payload.source_mode)
    direct_memory = extract_direct_memory(payload.message)
    if direct_memory:
        db.add(
            Memory(
                memory_type="user_instruction",
                content=direct_memory,
                importance=5,
                memory_metadata={"session_id": payload.session_id, "source": "direct_memory_command"},
            )
        )
        db.commit()
        memories = memory_context_for_chat(db, payload.message, payload.session_id)
        session_summary = get_session_summary(db, payload.session_id)
        return ChatResponse(
            answer=f"我记住了：{direct_memory}\n\n后面我会按这个规则来回答。你可以继续直接问产品、脚本或活动方案。",
            retrieved=[],
            memories=[memory.content for memory in memories],
            source_mode=source_mode,
            session_summary=session_summary.content if session_summary else None,
            auto_memory_saved=True,
            auto_memory=direct_memory,
        )

    chunks: list[dict] = []
    memories: list[Memory] = []
    web_results: list[dict] = []
    search_diagnostics: list[dict] = []
    question = payload.message

    if source_mode in ("knowledge_only", "knowledge_llm", "web_knowledge_llm"):
        chunks = search_chunks(db, payload.message, limit=payload.top_k)
        memories = memory_context_for_chat(db, payload.message, payload.session_id)
    elif source_mode == "llm_only":
        session_summary = get_session_summary(db, payload.session_id)
        memories = [session_summary] if session_summary else []

    if source_mode == "web_knowledge_llm":
        search_queries = build_chat_search_queries(payload.message)
        web_results, search_diagnostics = multi_search(search_queries, limit_per_query=4)
        web_chunks = [
            {
                "content": f"{item.get('title', '')}\n{item.get('snippet', '')}\n{item.get('url', '')}".strip(),
                "score": float(item.get("score") or 0.55),
                "metadata": {"title": item.get("title"), "url": item.get("url"), "provider": item.get("provider")},
                "source": "web_search",
            }
            for item in web_results[:5]
        ]
        chunks = web_chunks + chunks
        question = (
            "请结合公开联网搜索线索、我的知识库资料和长期记忆回答。"
            "请先综合多个搜索结果，不要只依赖单个来源。"
            "如果联网线索不足或互相矛盾，要明确说明哪些信息需要继续核实。\n\n"
            f"本次搜索词：{search_queries}\n\n"
            f"用户问题：{payload.message}"
        )
    elif source_mode == "knowledge_only":
        question = (
            "请只根据已检索到的我的知识库资料和长期记忆回答。"
            "不要使用外部联网信息，也不要把没有资料支撑的内容说成事实。"
            "如果资料不足，请直接说明知识库里暂时没有足够依据。\n\n"
            f"用户问题：{payload.message}"
        )
    elif source_mode == "llm_only":
        question = (
            "请像通用大模型一样自然回答，可以使用常识和推理。"
            "本次不要引用我的私有知识库资料。\n\n"
            f"用户问题：{payload.message}"
        )

    answer = generate_answer(question, chunks, memories, mode=payload.mode, history=history) or compose_answer(question, chunks, memories)
    auto_memory_saved = False
    auto_memory_text = None
    session_summary_updated = False
    session_summary_text = get_session_summary(db, payload.session_id)
    if payload.auto_memory and should_summarize_memory(payload.message, history):
        auto_memory_text = summarize_conversation_memory(history, payload.message, answer)
        if auto_memory_text:
            db.add(
                Memory(
                    memory_type="auto_summary",
                    content=auto_memory_text,
                    importance=4,
                    memory_metadata={"session_id": payload.session_id, "source": "chat_auto_summary"},
                )
            )
            db.commit()
            auto_memory_saved = True
    if payload.auto_memory and should_update_session_summary(history):
        previous_summary = session_summary_text.content if session_summary_text else None
        updated_summary = summarize_session_context(
            previous_summary=previous_summary,
            history=history,
            latest_question=payload.message,
            answer=answer,
        )
        if session_summary_text:
            session_summary_text.content = updated_summary
        else:
            session_summary_text = Memory(
                memory_type="session_summary",
                content=updated_summary,
                importance=4,
                memory_metadata={"session_id": payload.session_id, "source": "rolling_session_summary"},
            )
            db.add(session_summary_text)
        db.commit()
        session_summary_updated = True
        memories = memory_context_for_chat(db, payload.message, payload.session_id)
    return ChatResponse(
        answer=answer,
        retrieved=[
            SearchResult(
                content=chunk["content"],
                score=float(chunk["score"]),
                metadata=chunk["metadata"] or {},
                source=chunk.get("source"),
            )
            for chunk in chunks
        ],
        memories=[memory.content for memory in memories],
        source_mode=source_mode,
        session_summary=session_summary_text.content if session_summary_text else None,
        session_summary_updated=session_summary_updated,
        web_results=web_results,
        search_diagnostics=search_diagnostics,
        auto_memory_saved=auto_memory_saved,
        auto_memory=auto_memory_text,
    )


def normalize_source_mode(source_mode: str | None) -> str:
    allowed = {"knowledge_only", "llm_only", "knowledge_llm", "web_knowledge_llm"}
    return source_mode if source_mode in allowed else "knowledge_llm"


def build_chat_search_queries(message: str) -> list[str]:
    base = " ".join(message.strip().split())
    if not base:
        return []

    queries = [base]
    if any(keyword in base for keyword in ("对比", "竞品", "区别", "优势", "劣势", "为什么选择")):
        queries.extend(
            [
                f"{base} 产品介绍 成分 规格 价格",
                f"{base} 官方 旗舰店 用户评价",
                f"{base} 小红书 抖音 评价",
            ]
        )
    elif any(keyword in base for keyword in ("热点", "爆款", "脚本", "图文", "SEO", "关键词")):
        queries.extend(
            [
                f"{base} 抖音 爆款 案例",
                f"{base} 小红书 图文 标题",
                f"{base} 用户痛点 评论",
            ]
        )
    else:
        queries.extend([f"{base} 官方", f"{base} 评价", f"{base} 问答"])

    cleaned: list[str] = []
    seen = set()
    for query in queries:
        query = query.strip()
        if query and query not in seen:
            cleaned.append(query)
            seen.add(query)
    return cleaned[:4]


def should_summarize_memory(message: str, history: list[dict]) -> bool:
    keywords = ("记住", "以后", "我的要求", "我的偏好", "我们品牌", "不要", "必须", "固定", "规则", "长期")
    if any(keyword in message for keyword in keywords):
        return True
    user_turns = [item for item in history if item.get("role") == "user"]
    return len(user_turns) > 0 and len(user_turns) % 6 == 0


def should_update_session_summary(history: list[dict]) -> bool:
    user_turns = [item for item in history if item.get("role") == "user"]
    return len(user_turns) >= 6 and len(user_turns) % 4 == 0


def extract_direct_memory(message: str) -> str | None:
    text = message.strip()
    prefixes = (
        "记住：",
        "记住:",
        "记住，",
        "记住,",
        "记住 ",
        "请记住：",
        "请记住:",
        "请记住，",
        "请记住,",
        "以后你要记住：",
        "以后请记住：",
    )
    for prefix in prefixes:
        if text.startswith(prefix):
            memory = text[len(prefix):].strip()
            return memory[:500] if memory else None
    if text.startswith("以后") and any(keyword in text for keyword in ("回答", "写", "输出", "不要", "必须", "优先")):
        return text[:500]
    return None


@app.post("/workflows/content", response_model=ContentCreateResponse)
def content_workflow(payload: ContentCreateRequest, db: Session = Depends(get_db)) -> ContentCreateResponse:
    result = create_content_plan(payload, db)
    source_summary = {
        "trend_queries": result.trend_queries,
        "search_diagnostics": result.search_diagnostics,
        "trend_count": len(result.trends),
        "retrieved_count": len(result.retrieved),
        "viral_case_count": len(result.viral_cases),
    }
    history = save_generation_history(
        db,
        workflow="content",
        platform=payload.platform,
        product=payload.product,
        content_module=payload.content_module,
        goal=payload.goal,
        audience=payload.audience,
        keywords=payload.keywords,
        input_payload=payload.model_dump(),
        output_content=result.answer,
        source_summary=source_summary,
    )
    result.history_id = str(history.id)
    return result



@app.post("/workflows/benchmark")
async def benchmark_workflow(
    file: UploadFile | None = File(default=None),
    reference_text: str = Form(""),
    product: str = Form(""),
    platform: str = Form("小红书"),
    requirement: str = Form(""),
    audience: str = Form(""),
    keywords: str = Form(""),
    db: Session = Depends(get_db),
) -> dict:
    benchmark_parts: list[str] = []
    parsed_sources: list[dict] = []
    image_note = ""

    if reference_text.strip():
        benchmark_parts.append(reference_text.strip())
        parsed_sources.append({"source": "手动粘贴的对标内容", "type": "text", "chars": len(reference_text.strip())})

    if file and file.filename:
        raw = await file.read()
        suffix = Path(file.filename).suffix.lower()
        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            image_note = (
                "已收到图片文件，但当前版本还没有接入多模态视觉解析，"
                "不能直接识别图片里的画面和文字。请在“对标内容/拆解备注”里补充封面标题、正文、图片风格和你想模仿的点。"
            )
            parsed_sources.append({"source": file.filename, "type": "image", "chars": 0})
        else:
            try:
                parsed_documents = parse_file_bytes(file.filename, raw)
            except (ValueError, RuntimeError) as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            for title, content, metadata in parsed_documents[:8]:
                clipped = content.strip()[:3500]
                if clipped:
                    benchmark_parts.append(f"来源：{title}\n{clipped}")
                    parsed_sources.append(
                        {
                            "source": title,
                            "type": metadata.get("type") or suffix.lstrip(".") or "file",
                            "chars": len(clipped),
                        }
                    )

    benchmark_text = "\n\n".join(benchmark_parts).strip()
    if not benchmark_text and not image_note:
        raise HTTPException(status_code=400, detail="请先上传对标文件，或粘贴对标图文的标题、正文、结构和你想模仿的点。")

    query = " ".join(part for part in [product, platform, requirement, audience, keywords, benchmark_text[:500]] if part)
    product_chunks = search_chunks(db, query or product or requirement, limit=6)
    chunks = []
    if benchmark_text:
        chunks.append(
            {
                "content": benchmark_text[:6000],
                "score": 1.0,
                "metadata": {"source_type": "benchmark_reference"},
                "source": "对标作品资料",
            }
        )
    chunks.extend(product_chunks)
    memories = recent_memories(db, limit=6)
    question = (
        "请基于对标图文作品，为我的产品生成一套原创图文内容方案。\n"
        f"产品/主题：{product or '未填写'}\n"
        f"平台：{platform or '未填写'}\n"
        f"目标人群：{audience or '未填写'}\n"
        f"关键词/SEO词：{keywords or '未填写'}\n"
        f"我的需求：{requirement or '未填写'}\n\n"
        "输出要求：\n"
        "1. 先用短段落拆解对标作品为什么值得学。\n"
        "2. 给出适合我产品的封面标题、首图字幕、图文结构、每页/每段内容、配图建议、评论区引导和转化话术。\n"
        "3. 明确哪些是可以模仿的结构，哪些不能照搬。\n"
        "4. 遵守产品资料和长期记忆里的禁用表达，不要夸大功效。"
    )
    if image_note:
        question += f"\n\n图片处理提示：{image_note}"
    answer = generate_answer(question, chunks, memories, mode="benchmark") or compose_answer(question, chunks, memories)
    history = save_generation_history(
        db,
        workflow="benchmark",
        platform=platform,
        product=product,
        content_module="对标图文创作",
        goal=requirement[:120] if requirement else "对标创作",
        audience=audience,
        keywords=keywords,
        input_payload={
            "reference_text": reference_text[:3000],
            "product": product,
            "platform": platform,
            "requirement": requirement,
            "audience": audience,
            "keywords": keywords,
            "parsed_sources": parsed_sources,
        },
        output_content=answer,
        source_summary={
            "image_note": image_note,
            "parsed_sources": parsed_sources,
            "retrieved_count": len(product_chunks),
        },
    )
    return {
        "history_id": str(history.id),
        "answer": answer,
        "image_note": image_note,
        "parsed_sources": parsed_sources,
        "retrieved": product_chunks,
    }
