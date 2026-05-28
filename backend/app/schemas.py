from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    category: str | None = None
    target_audience: str | None = None
    selling_points: str | None = None
    cautions: str | None = None
    knowledge_text: str | None = None


class ProductOut(ProductCreate):
    id: UUID


class MemoryCreate(BaseModel):
    memory_type: str = Field(default="user_preference")
    content: str
    importance: int = Field(default=3, ge=1, le=5)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    mode: str = Field(default="assistant")
    source_mode: str = Field(default="knowledge_llm")
    top_k: int = Field(default=5, ge=1, le=12)
    history: list["ConversationMessage"] = Field(default_factory=list)
    auto_memory: bool = True


class ConversationMessage(BaseModel):
    role: str
    content: str


class SearchResult(BaseModel):
    content: str
    score: float
    metadata: dict
    source: str | None = None


class ChatResponse(BaseModel):
    answer: str
    retrieved: list[SearchResult]
    memories: list[str]
    source_mode: str = "knowledge_llm"
    session_summary: str | None = None
    session_summary_updated: bool = False
    web_results: list[dict] = Field(default_factory=list)
    search_diagnostics: list[dict] = Field(default_factory=list)
    auto_memory_saved: bool = False
    auto_memory: str | None = None


class FolderIngestRequest(BaseModel):
    folder_path: str
    reset: bool = False


class FolderAnalyzeRequest(BaseModel):
    folder_path: str
    instruction: str = "请分析这个文件夹里的资料，总结核心内容、产品运营机会和需要注意的风险。"
    max_documents: int = Field(default=10, ge=1, le=30)


class FolderIngestResponse(BaseModel):
    saved: bool
    count: int
    files: list[dict]


class ViralCaseCreate(BaseModel):
    platform: str | None = None
    product: str | None = None
    title: str | None = None
    url: str | None = None
    author: str | None = None
    content: str
    metrics: dict = Field(default_factory=dict)
    tags: str | None = None


class ViralCaseOut(ViralCaseCreate):
    id: UUID
    analysis: str | None = None


class GenerationHistoryOut(BaseModel):
    id: UUID
    workflow: str
    platform: str | None = None
    product: str | None = None
    content_module: str | None = None
    goal: str | None = None
    audience: str | None = None
    keywords: str | None = None
    input_payload: dict = Field(default_factory=dict)
    output_content: str
    source_summary: dict = Field(default_factory=dict)
    status: str = "draft"
    converted_case_id: UUID | None = None
    created_at: datetime | None = None


class HistoryToCaseRequest(BaseModel):
    title: str | None = None
    url: str | None = None
    author: str | None = None
    metrics: dict = Field(default_factory=dict)
    tags: str | None = None
    notes: str | None = None
