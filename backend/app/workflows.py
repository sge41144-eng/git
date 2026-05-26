from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.llm import generate_competitor_analysis, generate_content_plan
from app.models import Memory, ViralCase
from app.rag import recent_memories, search_chunks
from app.web_search import build_trend_queries, multi_search, summarize_search_results


class ContentCreateRequest(BaseModel):
    product: str
    platform: str = Field(default="抖音")
    goal: str = Field(default="种草转化")
    audience: str = ""
    content_module: str = Field(default="short_video")
    keywords: str = ""
    seo_goal: str = ""
    image_requirements: str = ""
    reference_style: str = ""
    extra_requirements: str = ""
    top_k: int = Field(default=6, ge=1, le=12)
    search_limit: int = Field(default=5, ge=1, le=10)


class ContentCreateResponse(BaseModel):
    history_id: str | None = None
    answer: str
    retrieved: list[dict]
    trends: list[dict]
    trend_queries: list[str]
    search_diagnostics: list[dict] = Field(default_factory=list)
    viral_cases: list[dict] = Field(default_factory=list)
    memories: list[str]


class CompetitorCompareRequest(BaseModel):
    our_product: str
    competitor_brand: str
    competitor_product: str = ""
    platform: str = Field(default="全网")
    compare_focus: str = Field(default="成分、含量、卖点、适用人群、价格、规格、使用场景")
    audience: str = ""
    output_mode: str = Field(default="产品优劣势对比")
    top_k: int = Field(default=6, ge=1, le=12)
    search_limit: int = Field(default=5, ge=1, le=10)


class CompetitorCompareResponse(BaseModel):
    history_id: str | None = None
    answer: str
    retrieved: list[dict]
    competitor_results: list[dict]
    search_queries: list[str]
    search_diagnostics: list[dict] = Field(default_factory=list)
    memories: list[str]


def create_content_plan(payload: ContentCreateRequest, db: Session) -> ContentCreateResponse:
    query = " ".join(
        [
            payload.product,
            payload.platform,
            payload.goal,
            payload.audience,
            payload.content_module,
            payload.keywords,
            payload.seo_goal,
            payload.reference_style,
            payload.extra_requirements,
        ]
    )
    chunks = search_chunks(db, query, limit=payload.top_k)
    memories = recent_memories(db)

    trend_queries = build_trend_queries(
        platform=payload.platform,
        product=payload.product,
        goal=payload.goal,
        audience=payload.audience,
        content_module=payload.content_module,
        keywords=payload.keywords,
        seo_goal=payload.seo_goal,
    )
    trends, search_diagnostics = multi_search(trend_queries, limit_per_query=payload.search_limit)
    trends = trends[: payload.search_limit * len(trend_queries)]
    trend_summary = summarize_search_results(trends)
    viral_cases = find_relevant_viral_cases(db, query, limit=5)
    case_summary = summarize_viral_cases(viral_cases)
    combined_trend_summary = f"公开搜索线索：\n{trend_summary}\n\n手动投喂的爆款/竞品案例：\n{case_summary}"

    answer = generate_content_plan(
        product=payload.product,
        platform=payload.platform,
        goal=payload.goal,
        audience=payload.audience,
        content_module=payload.content_module,
        keywords=payload.keywords,
        seo_goal=payload.seo_goal,
        image_requirements=payload.image_requirements,
        reference_style=payload.reference_style,
        extra_requirements=payload.extra_requirements,
        chunks=chunks,
        memories=memories,
        trend_summary=combined_trend_summary,
    )
    return ContentCreateResponse(
        answer=answer,
        retrieved=chunks,
        trends=trends,
        trend_queries=trend_queries,
        search_diagnostics=search_diagnostics,
        viral_cases=viral_cases,
        memories=[memory.content for memory in memories],
    )


def create_competitor_compare(payload: CompetitorCompareRequest, db: Session) -> CompetitorCompareResponse:
    competitor_name = " ".join(
        part for part in [payload.competitor_brand, payload.competitor_product] if part.strip()
    ).strip()
    query = " ".join(
        [
            payload.our_product,
            competitor_name,
            payload.platform,
            payload.compare_focus,
            payload.audience,
            payload.output_mode,
        ]
    )
    chunks = search_chunks(db, query, limit=payload.top_k)
    memories = recent_memories(db, limit=8)
    search_queries = build_competitor_queries(
        competitor_name=competitor_name,
        our_product=payload.our_product,
        platform=payload.platform,
        focus=payload.compare_focus,
    )
    competitor_results, search_diagnostics = multi_search(search_queries, limit_per_query=payload.search_limit)
    competitor_results = competitor_results[: payload.search_limit * len(search_queries)]
    competitor_summary = summarize_search_results(competitor_results)
    answer = generate_competitor_analysis(
        our_product=payload.our_product,
        competitor_name=competitor_name,
        platform=payload.platform,
        compare_focus=payload.compare_focus,
        audience=payload.audience,
        output_mode=payload.output_mode,
        chunks=chunks,
        memories=memories,
        competitor_summary=competitor_summary,
    )
    return CompetitorCompareResponse(
        answer=answer,
        retrieved=chunks,
        competitor_results=competitor_results,
        search_queries=search_queries,
        search_diagnostics=search_diagnostics,
        memories=[memory.content for memory in memories],
    )


def build_competitor_queries(*, competitor_name: str, our_product: str, platform: str, focus: str) -> list[str]:
    product_terms = " ".join(part for part in [competitor_name, our_product] if part)
    platform_prefix = "" if platform in {"全网", "不限", ""} else platform
    return [
        " ".join(part for part in [platform_prefix, competitor_name, "产品 介绍 卖点 成分"] if part),
        " ".join(part for part in [platform_prefix, competitor_name, "价格 规格 适用人群"] if part),
        " ".join(part for part in [platform_prefix, competitor_name, "成分表 含量 配料"] if part),
        " ".join(part for part in [platform_prefix, competitor_name, "用户评价 口碑 评论"] if part),
        " ".join(part for part in [product_terms, "对比 优势 差异"] if part),
    ]


def dedupe_results(results: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for result in results:
        key = result.get("url") or result.get("title")
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(result)
    return unique


def find_relevant_viral_cases(db: Session, query: str, limit: int = 5) -> list[dict]:
    query_lower = query.lower()
    rows = db.query(ViralCase).order_by(ViralCase.created_at.desc()).limit(80).all()
    scored = []
    for row in rows:
        text = " ".join(
            value or ""
            for value in [row.platform, row.product, row.title, row.author, row.content, row.analysis, row.tags]
        )
        score = sum(1 for term in query_lower.split() if term and term in text.lower())
        if row.product and row.product.lower() in query_lower:
            score += 3
        if row.platform and row.platform.lower() in query_lower:
            score += 2
        scored.append((score, row))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        {
            "id": str(row.id),
            "platform": row.platform,
            "product": row.product,
            "title": row.title,
            "url": row.url,
            "author": row.author,
            "content": row.content,
            "metrics": row.metrics or {},
            "analysis": row.analysis,
            "tags": row.tags,
            "score": score,
        }
        for score, row in scored[:limit]
        if score > 0 or len(scored) <= limit
    ]


def summarize_viral_cases(cases: list[dict]) -> str:
    if not cases:
        return "暂无匹配的手动爆款/竞品案例。"
    lines = []
    for index, case in enumerate(cases, 1):
        lines.append(
            f"{index}. 平台：{case.get('platform') or ''} 产品：{case.get('product') or ''}\n"
            f"   标题：{case.get('title') or ''}\n"
            f"   内容：{str(case.get('content') or '')[:500]}\n"
            f"   数据：{case.get('metrics') or {}}\n"
            f"   拆解：{case.get('analysis') or ''}"
        )
    return "\n".join(lines)
