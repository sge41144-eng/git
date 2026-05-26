import json
import urllib.error
import urllib.request

from app.config import settings
from app.models import Memory


class BailianChatClient:
    def __init__(self) -> None:
        if not settings.dashscope_api_key:
            raise RuntimeError("DASHSCOPE_API_KEY is required when LLM_PROVIDER=bailian")
        self.url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    def complete(
        self,
        *,
        question: str,
        chunks: list[dict],
        memories: list[Memory],
        mode: str = "qa",
        history: list[dict] | None = None,
    ) -> str:
        context = "\n\n".join(
            f"[资料 {index + 1} | 来源：{chunk.get('source') or '知识库'} | 相关度 {chunk['score']:.3f}]\n{chunk['content']}"
            for index, chunk in enumerate(chunks)
        )
        memory_text = "\n".join(f"- {memory.content}" for memory in memories) or "暂无长期记忆。"
        history_text = format_history(history or [])
        mode_instruction = mode_prompt(mode)
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一个中文产品运营智能体。你需要基于给定产品资料、长期记忆和本轮上下文回答，"
                    "不能编造资料库没有的信息，但可以使用明确的常识性成分推理，并要说明推理边界。"
                    "如果用户问题明确说明本次是通用大模型回答、不要引用私有知识库或资料为空，则可以像通用大模型一样使用常识和推理回答，"
                    "但不能伪装成已经读取了知识库或联网资料。"
                    "请根据用户当前意图自然回应，不要机械套固定模板；"
                    "如果用户要求脚本、活动方案或运营策略，要输出结构化内容。"
                    "特别注意：资料中的“禁用表达、禁忌词汇、禁止说法”只表示客服或销售不能这样表述，"
                    "不能当作产品事实、适用限制或禁忌人群。遇到这类内容时，应优先依据“用法用量、注意事项、"
                    "适用人群、推荐话术/可用表达”等字段回答。"
                    "遇到成分、过敏原、乳糖、婴幼儿、用法用量等安全/合规问题时，不要因为配料表未单列某成分就断言绝对不含；"
                    "如果原料本身天然可能含有某成分，要用谨慎话术说明“配料表未额外添加/未单列，但原料天然可能含有”，"
                    "并建议敏感人群少量尝试或咨询专业人士。"
                    f"\n\n当前回答模式：{mode_instruction}"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"长期记忆：\n{memory_text}\n\n"
                    f"本轮对话上下文：\n{history_text}\n\n"
                    f"已检索资料：\n{context}\n\n"
                    f"用户问题：{question}"
                ),
            },
        ]
        payload = {
            "model": settings.llm_model,
            "messages": messages,
            "temperature": 0.7,
        }
        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.dashscope_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Bailian chat request failed: {exc.code} {detail}") from exc
        return result["choices"][0]["message"]["content"]


def mode_prompt(mode: str) -> str:
    prompts = {
        "assistant": "运营助手模式。像运营同事一样自然对话；需要事实时再引用依据，需要创作时直接给可执行方案。",
        "qa": "产品问答模式。优先直接回答用户问题；只有涉及安全、用法、合规时再补充依据、客服话术和注意事项。",
        "script": "内容脚本模式。输出短视频脚本，包含开头钩子、场景、卖点植入、镜头建议、口播、结尾转化。",
        "benchmark": "对标图文创作模式。先拆解对标作品的封面、标题、结构、卖点表达、转化路径和可模仿格式，再结合用户产品生成原创图文方案；禁止照搬竞品措辞、品牌名、承诺和不可验证效果。",
        "campaign": "活动策划模式。输出活动主题、人群洞察、机制、内容节奏、执行清单、风险提醒。",
        "customer_service": (
            "客服话术模式。优先输出一段可直接复制给客户的自然话术；随后只在必要时列出注意事项和不能说的话。"
            "不要机械套“客服话术/不能说的话”标题。涉及乳糖、过敏、婴幼儿、用法用量时要谨慎，"
            "允许基于原料属性做合理推理：例如牛初乳粉作为乳来源原料，可能天然含乳糖；即使配料表没有额外添加或单列乳糖，也不能说绝对不含乳糖。"
        ),
    }
    return prompts.get(mode, prompts["qa"])


def format_history(history: list[dict], limit: int = 10) -> str:
    if not history:
        return "暂无本轮上下文。"
    clipped = history[-limit:]
    lines = []
    for item in clipped:
        role = "用户" if item.get("role") == "user" else "助手"
        content = str(item.get("content", "")).strip()
        if content:
            lines.append(f"{role}：{content[:800]}")
    return "\n".join(lines) or "暂无本轮上下文。"


def generate_answer(
    question: str,
    chunks: list[dict],
    memories: list[Memory],
    mode: str = "qa",
    history: list[dict] | None = None,
) -> str | None:
    if settings.llm_provider == "bailian":
        return BailianChatClient().complete(question=question, chunks=chunks, memories=memories, mode=mode, history=history)
    return None


def summarize_conversation_memory(history: list[dict], latest_question: str, answer: str) -> str | None:
    if settings.llm_provider != "bailian":
        return heuristic_memory_summary(history, latest_question, answer)

    history_text = format_history(history, limit=12)
    client = BailianChatClient()
    messages = [
        {
            "role": "system",
            "content": (
                "你是运营智能体的长期记忆整理器。只提取未来长期有用的信息，"
                "例如用户偏好、品牌规则、产品事实、禁用表达、固定工作流、复盘结论。"
                "不要记录一次性的闲聊、临时问题、无明确价值的信息。"
                "如果没有值得保存的长期记忆，只输出：无需保存"
            ),
        },
        {
            "role": "user",
            "content": (
                f"本轮对话：\n{history_text}\n\n"
                f"最新用户问题：{latest_question}\n\n"
                f"助手回答：{answer[:1200]}\n\n"
                "请输出一条简洁的长期记忆，80字以内。"
            ),
        },
    ]
    payload = {"model": settings.llm_model, "messages": messages, "temperature": 0.2}
    request = urllib.request.Request(
        client.url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.dashscope_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError:
        return heuristic_memory_summary(history, latest_question, answer)
    summary = result["choices"][0]["message"]["content"].strip()
    if not summary or "无需保存" in summary:
        return None
    return summary[:300]


def heuristic_memory_summary(history: list[dict], latest_question: str, answer: str) -> str | None:
    text = latest_question.strip()
    keywords = ("记住", "以后", "我的", "我们", "偏好", "不要", "必须", "固定", "品牌", "规则")
    if any(keyword in text for keyword in keywords):
        return f"用户长期要求：{text[:120]}"
    if len(history) >= 8:
        return f"阶段对话摘要：用户围绕产品运营助手持续讨论，最近关注：{text[:90]}"
    return None


def generate_content_plan(
    *,
    product: str,
    platform: str,
    goal: str,
    audience: str,
    content_module: str,
    keywords: str,
    seo_goal: str,
    image_requirements: str,
    reference_style: str,
    extra_requirements: str,
    chunks: list[dict],
    memories: list[Memory],
    trend_summary: str,
) -> str:
    if settings.llm_provider != "bailian":
        return "当前未接入大模型，无法生成趋势驱动内容方案。"

    context = "\n\n".join(
        f"[资料 {index + 1} | 来源：{chunk.get('source') or '知识库'} | 相关度 {chunk['score']:.3f}]\n{chunk['content']}"
        for index, chunk in enumerate(chunks)
    )
    memory_text = "\n".join(f"- {memory.content}" for memory in memories) or "暂无长期记忆。"
    client = BailianChatClient()
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个资深内容运营、SEO图文策划和短视频投放策划。你需要结合产品知识库、长期记忆、"
                "公开搜索到的热点/爆款线索、用户投喂的爆款案例，为用户生成有搜索流量、推荐流量或转化潜力的内容方案。"
                "必须避免把禁用表达当事实依据。输出要具体、可拍、可发布、可执行，不能只写空泛建议。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"产品：{product}\n"
                f"平台：{platform}\n"
                f"目标：{goal}\n"
                f"目标人群：{audience or '未指定'}\n"
                f"创作模块：{content_module}\n"
                f"关键词/SEO词：{keywords or '未指定'}\n"
                f"SEO搜索目标：{seo_goal or '未指定'}\n"
                f"产品实拍/图片要求：{image_requirements or '未指定'}\n"
                f"参考/模仿格式：{reference_style or '未指定'}\n"
                f"额外要求：{extra_requirements or '无'}\n\n"
                f"长期记忆：\n{memory_text}\n\n"
                f"产品资料：\n{context}\n\n"
                f"公开热点/爆款搜索线索：\n{trend_summary}\n\n"
                "请根据创作模块输出对应方案：\n"
                "A. 如果是 SEO图文：输出关键词分组、搜索意图、标题矩阵、图文大纲、首图建议、正文段落、FAQ、内链/标签建议。\n"
                "B. 如果是产品实拍图文：输出拍摄清单、构图、光线/场景、每张图的字幕、图文发布文案、卖点植入方式。\n"
                "C. 如果是字幕/口播：输出开头钩子、字幕分段、口播稿、停顿节奏、屏幕文字和CTA。\n"
                "D. 如果是推荐种草：输出人群场景、推荐理由、对比角度、真实体验口吻、风险提醒和转化话术。\n"
                "E. 如果是爆款格式模仿：先拆解参考格式，再给可复用模板，最后套用到当前产品生成3个版本。\n"
                "F. 如果是短视频：输出标题、前3秒钩子、分镜/画面、口播、产品植入、结尾CTA、爆款评分。\n"
                "所有模块都必须额外输出：合规风险、禁用/替代表达、素材清单、可直接发布的成品文案。\n"
            ),
        },
    ]
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "temperature": 0.85,
    }
    request = urllib.request.Request(
        client.url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.dashscope_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Bailian content plan request failed: {exc.code} {detail}") from exc
    return result["choices"][0]["message"]["content"]


def generate_competitor_analysis(
    *,
    our_product: str,
    competitor_name: str,
    platform: str,
    compare_focus: str,
    audience: str,
    output_mode: str,
    chunks: list[dict],
    memories: list[Memory],
    competitor_summary: str,
) -> str:
    if settings.llm_provider != "bailian":
        return "当前未接入大模型，无法生成竞品对比分析。"

    context = "\n\n".join(
        f"[我方资料 {index + 1} | 来源：{chunk.get('source') or '知识库'} | 相关度 {chunk['score']:.3f}]\n{chunk['content']}"
        for index, chunk in enumerate(chunks)
    )
    memory_text = "\n".join(f"- {memory.content}" for memory in memories) or "暂无长期记忆。"
    client = BailianChatClient()
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个中文产品竞品对比分析助手。你的唯一目标是回答：我方产品相比竞品有什么优势、有什么劣势、"
                "客户为什么应该选择我方而不是竞品。必须区分我方资料、竞品公开线索和推测，不要把搜索摘要当作绝对事实。"
                "不要输出客服话术、内容运营建议、脚本、标题、评论区回复、合规风险大段分析或营销方案。"
                "表达要短、清楚、像给老板看的产品对比结论。不要贬低竞品，不要夸大不可验证效果。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"我方产品/主题：{our_product}\n"
                f"竞品：{competitor_name}\n"
                f"平台/渠道：{platform}\n"
                f"对比重点：{compare_focus}\n"
                f"目标人群：{audience or '未指定'}\n"
                f"输出用途：{output_mode or '运营策略'}\n\n"
                f"长期记忆：\n{memory_text}\n\n"
                f"我方产品资料：\n{context or '暂无我方资料，请提醒用户补充。'}\n\n"
                f"公开搜索到的竞品线索：\n{competitor_summary or '未检索到有效公开线索。'}\n\n"
                "请严格按下面格式输出，禁止增加客服话术、内容运营、脚本、合规风险等无关板块：\n\n"
                "一、核心结论\n"
                "用2-3句话说明：我方是否有明显优势，优势主要集中在哪些方面，哪些地方还需要谨慎。\n\n"
                "二、我方相对竞品的优势\n"
                "只列3-6条。每条格式为：优势点｜为什么是优势｜依据来自哪里。\n\n"
                "三、我方可能的劣势或不确定点\n"
                "只列2-5条。没有确凿资料时要写“需要核实”，不要强行下结论。\n\n"
                "四、客户为什么选择我方\n"
                "列出3-5条可用于内部销售判断的选择理由，重点回答“为什么不选其他产品而选我方”。\n\n"
                "五、还需要补充核实的信息\n"
                "只列最关键的竞品信息，例如成分表、含量、规格、价格、适用人群、真实评价。"
            ),
        },
    ]
    payload = {"model": settings.llm_model, "messages": messages, "temperature": 0.65}
    request = urllib.request.Request(
        client.url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.dashscope_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Bailian competitor analysis request failed: {exc.code} {detail}") from exc
    return result["choices"][0]["message"]["content"]
