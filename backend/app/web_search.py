from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from html import unescape

from app.config import settings


MODULE_LABELS = {
    "short_video": "短视频脚本",
    "seo_article": "SEO 图文",
    "product_photo_post": "产品实拍图文",
    "caption_copy": "字幕口播文案",
    "recommendation_post": "推荐种草",
    "viral_format_mimic": "爆款格式模仿",
}


def web_search(query: str, limit: int = 6) -> list[dict]:
    """Best-effort public web search without an extra API key.

    This is enough for MVP trend discovery. Later we can replace or augment it
    with official/paid data providers such as 巨量算数、磁力引擎、蝉妈妈、飞瓜、新抖.
    """
    if not query.strip():
        return []
    results, _ = web_search_with_diagnostics(query, limit=limit)
    return results


def multi_search(queries: list[str], limit_per_query: int = 5) -> tuple[list[dict], list[dict]]:
    all_results: list[dict] = []
    diagnostics: list[dict] = []
    for query in queries:
        results, detail = web_search_with_diagnostics(query, limit=limit_per_query)
        diagnostics.append({"query": query, "count": len(results), "ok": bool(results), **detail})
        all_results.extend({**item, "query": query} for item in results)
    return dedupe_search_results(all_results), diagnostics


def web_search_with_diagnostics(query: str, limit: int = 6) -> tuple[list[dict], dict]:
    if not query.strip():
        return [], {"provider": "none", "reason": "搜索词为空"}

    provider_errors: list[str] = []
    provider_details: list[dict] = []
    all_results: list[dict] = []
    for provider, search_fn in (
        ("baidu", baidu_html_search),
        ("sogou", sogou_html_search),
        ("bing", bing_html_search),
        ("duckduckgo", duckduckgo_html_search),
    ):
        raw_results, error = search_fn(query, limit=limit, return_error=True)
        if raw_results:
            normalized = normalize_results(raw_results, provider=provider)
            all_results.extend(normalized)
            provider_details.append({"provider": provider, "ok": True, "count": len(normalized), "reason": "公开搜索成功"})
            continue
        provider_details.append({"provider": provider, "ok": False, "count": 0, "reason": error or "无结果"})
        provider_errors.append(f"{provider}={error or '无结果'}")

    if all_results:
        merged = dedupe_search_results(all_results)[:limit]
        success_providers = [item["provider"] for item in provider_details if item["ok"]]
        return merged, {
            "provider": ",".join(success_providers),
            "reason": f"多源公开搜索成功：{','.join(success_providers)}",
            "providers": provider_details,
        }

    return [], {
        "provider": "baidu,sogou,bing,duckduckgo",
        "reason": "公开搜索连接失败或无结果：" + "；".join(provider_errors),
        "providers": provider_details,
    }
def baidu_html_search(query: str, limit: int = 6, return_error: bool = False):
    url = "https://www.baidu.com/s?" + urllib.parse.urlencode({"wd": query})
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
        },
    )
    try:
        with open_url(request, timeout=8) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return ([], str(exc)) if return_error else []

    results = []
    blocks = re.findall(r'<div[^>]+class="[^"]*(?:result|c-container)[^"]*".*?</div>\s*</div>', html, flags=re.S)
    if not blocks:
        blocks = re.findall(r'<h3[^>]*>.*?</h3>.*?(?=<h3|$)', html, flags=re.S)
    for block in blocks:
        title_match = re.search(r'<h3[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?</h3>', block, flags=re.S)
        if not title_match:
            title_match = re.search(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, flags=re.S)
        if not title_match:
            continue
        snippet = clean_html(re.sub(r"<h3.*?</h3>", "", block, flags=re.S))[:300]
        results.append(
            {
                "title": clean_html(title_match.group(2)),
                "url": unescape(title_match.group(1)),
                "snippet": snippet,
            }
        )
        if len(results) >= limit:
            break
    return (results, "") if return_error else results


def sogou_html_search(query: str, limit: int = 6, return_error: bool = False):
    url = "https://www.sogou.com/web?" + urllib.parse.urlencode({"query": query})
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
        },
    )
    try:
        with open_url(request, timeout=8) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return ([], str(exc)) if return_error else []

    results = []
    blocks = re.findall(r'<div[^>]+class="[^"]*(?:vrwrap|results|rb)[^"]*".*?(?=<div[^>]+class="[^"]*(?:vrwrap|results|rb)|$)', html, flags=re.S)
    if not blocks:
        blocks = re.findall(r'<h3[^>]*>.*?</h3>.*?(?=<h3|$)', html, flags=re.S)
    for block in blocks:
        title_match = re.search(r'<h3[^>]*>.*?<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?</h3>', block, flags=re.S)
        if not title_match:
            title_match = re.search(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, flags=re.S)
        if not title_match:
            continue
        snippet = clean_html(re.sub(r"<h3.*?</h3>", "", block, flags=re.S))[:300]
        results.append(
            {
                "title": clean_html(title_match.group(2)),
                "url": unescape(title_match.group(1)),
                "snippet": snippet,
            }
        )
        if len(results) >= limit:
            break
    return (results, "") if return_error else results

def duckduckgo_html_search(query: str, limit: int = 6, return_error: bool = False):
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )
    try:
        with open_url(request, timeout=20) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return ([], str(exc)) if return_error else []

    results = []
    blocks = re.findall(r'<div class="result results_links.*?</div>\s*</div>', html, flags=re.S)
    for block in blocks:
        title_match = re.search(r'class="result__a" href="([^"]+)".*?>(.*?)</a>', block, flags=re.S)
        snippet_match = re.search(r'class="result__snippet".*?>(.*?)</a>|class="result__snippet".*?>(.*?)</div>', block, flags=re.S)
        if not title_match:
            continue
        raw_url = unescape(title_match.group(1))
        title = clean_html(title_match.group(2))
        snippet = clean_html((snippet_match.group(1) or snippet_match.group(2)) if snippet_match else "")
        results.append({"title": title, "url": unwrap_duckduckgo_url(raw_url), "snippet": snippet})
        if len(results) >= limit:
            break
    return (results, "") if return_error else results


def bing_html_search(query: str, limit: int = 6) -> list[dict]:
    results, _ = bing_html_search(query, limit=limit, return_error=True)
    return results


def bing_html_search(query: str, limit: int = 6, return_error: bool = False):
    url = "https://www.bing.com/search?" + urllib.parse.urlencode({"q": query})
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    )
    try:
        with open_url(request, timeout=20) as response:
            html = response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return ([], str(exc)) if return_error else []

    results = []
    blocks = re.findall(r"<li class=\"b_algo\".*?</li>", html, flags=re.S)
    for block in blocks:
        title_match = re.search(r"<h2.*?><a href=\"([^\"]+)\".*?>(.*?)</a></h2>", block, flags=re.S)
        snippet_match = re.search(r"<p>(.*?)</p>", block, flags=re.S)
        if not title_match:
            continue
        results.append(
            {
                "title": clean_html(title_match.group(2)),
                "url": unescape(title_match.group(1)),
                "snippet": clean_html(snippet_match.group(1) if snippet_match else ""),
            }
        )
        if len(results) >= limit:
            break
    return (results, "") if return_error else results


def open_url(request: urllib.request.Request, timeout: int = 20):
    if settings.search_proxy:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": settings.search_proxy, "https": settings.search_proxy})
        )
        return opener.open(request, timeout=timeout)
    return urllib.request.urlopen(request, timeout=timeout)


def build_trend_queries(
    *,
    platform: str,
    product: str,
    goal: str,
    audience: str = "",
    content_module: str = "",
    keywords: str = "",
    seo_goal: str = "",
) -> list[str]:
    platform = clean_query_part(platform)
    product = clean_query_part(product)
    goal = clean_query_part(goal)
    audience = clean_query_part(audience)
    module = MODULE_LABELS.get(content_module, clean_query_part(content_module))
    keyword_text = clean_query_part(keywords)
    seo_text = clean_query_part(seo_goal)

    product_terms = " ".join(part for part in [product, keyword_text] if part)
    base = " ".join(part for part in [platform, product_terms, goal, audience] if part)
    queries = [
        f"{base} 热点 爆款",
        f"{platform} {product_terms} 用户痛点 评论",
        f"{platform} {product_terms} 种草 文案 案例",
        f"{platform} {product_terms} {module} 爆款结构",
        f"{platform} {product_terms} 近期趋势",
    ]
    if seo_text:
        queries.append(f"{product_terms} {seo_text} 搜索词 问答")
    return dedupe_queries(queries)


def summarize_search_results(results: list[dict]) -> str:
    if not results:
        return (
            "未检索到可靠的公开搜索结果。请使用通用爆款结构，并提示需要人工补充平台实时热点或竞品数据。"
        )
    lines = []
    for index, item in enumerate(results, 1):
        lines.append(
            f"{index}. 标题：{item.get('title', '')}\n"
            f"   摘要：{item.get('snippet', '')}\n"
            f"   来源：{item.get('url', '')}\n"
            f"   相关度：{item.get('score', 0):.2f}"
        )
    return "\n".join(lines)


def normalize_results(results: list[dict], provider: str) -> list[dict]:
    normalized = []
    for item in results:
        title = item.get("title", "").strip()
        url = item.get("url", "").strip()
        snippet = item.get("snippet", "").strip()
        if not title and not snippet:
            continue
        normalized.append(
            {
                "title": title,
                "url": url,
                "snippet": snippet,
                "provider": provider,
                "score": score_search_result(title, snippet, url),
            }
        )
    normalized.sort(key=lambda item: item["score"], reverse=True)
    return normalized


def score_search_result(title: str, snippet: str, url: str) -> float:
    text = f"{title} {snippet}".lower()
    score = 0.5
    for keyword in ("爆款", "热点", "抖音", "快手", "小红书", "短视频", "脚本", "案例", "趋势", "评论"):
        if keyword.lower() in text:
            score += 0.08
    if url and not any(domain in url for domain in ("zhihu.com/question", "tieba.baidu.com")):
        score += 0.08
    return min(score, 1.0)


def dedupe_search_results(results: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for result in results:
        key = normalize_url(result.get("url", "")) or result.get("title", "")
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(result)
    unique.sort(key=lambda item: item.get("score", 0), reverse=True)
    return unique


def unwrap_duckduckgo_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    if "uddg" in query and query["uddg"]:
        return query["uddg"][0]
    return url


def normalize_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if not parsed.netloc:
        return url
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", "", ""))


def clean_html(value: str) -> str:
    value = re.sub(r"<.*?>", "", value, flags=re.S)
    value = unescape(value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_query_part(value: str) -> str:
    value = MODULE_LABELS.get(value, value or "")
    value = re.sub(r"\b(short_video|seo_article|product_photo_post|caption_copy|recommendation_post|viral_format_mimic)\b", " ", value)
    value = re.sub(r"[_|,，、/\\]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def dedupe_queries(queries: list[str]) -> list[str]:
    seen = set()
    cleaned = []
    for query in queries:
        query = clean_query_part(query)
        if query and query not in seen:
            cleaned.append(query)
            seen.add(query)
    return cleaned


def results_to_json(results: list[dict]) -> str:
    return json.dumps(results, ensure_ascii=False, indent=2)
