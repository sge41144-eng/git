HOME_HTML = r"""
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>产品运营智能体</title>
    <style>
      * { box-sizing: border-box; }
      :root {
        --bg: #eef2f7;
        --panel: #ffffff;
        --line: #d8dee8;
        --text: #101828;
        --muted: #667085;
        --primary: #1b64d8;
        --primary-dark: #1552b1;
        --soft: #eff6ff;
        --soft-line: #c9ddff;
        --ok: #0f766e;
        --danger: #b42318;
        --sidebar: #111827;
        --sidebar-muted: #aab3c2;
      }
      body {
        margin: 0;
        color: var(--text);
        background: var(--bg);
        font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
      }
      .app-shell {
        display: grid;
        grid-template-columns: 248px minmax(0, 1fr);
        min-height: 100vh;
      }
      .sidebar {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        padding: 18px 14px;
        background: var(--sidebar);
        color: #fff;
      }
      .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 8px 18px;
        border-bottom: 1px solid rgba(255,255,255,.1);
      }
      .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
        border-radius: 8px;
        background: #fff;
        color: var(--primary);
        font-weight: 800;
        letter-spacing: 0;
      }
      .brand-title { font-size: 16px; font-weight: 700; line-height: 1.2; }
      .brand-subtitle { margin-top: 2px; color: var(--sidebar-muted); font-size: 12px; }
      .sidebar-foot {
        margin-top: auto;
        padding: 14px 8px 4px;
        color: var(--sidebar-muted);
        font-size: 12px;
        line-height: 1.6;
      }
      .sidebar-foot a { color: #dbeafe; }
      .workspace {
        display: flex;
        flex-direction: column;
        min-width: 0;
        min-height: 100vh;
      }
      .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        padding: 18px 24px;
        background: var(--panel);
        border-bottom: 1px solid var(--line);
      }
      h1 { margin: 0 0 4px; font-size: 22px; letter-spacing: 0; }
      h2 { margin: 0; font-size: 18px; letter-spacing: 0; }
      h3 { margin: 18px 0 8px; font-size: 15px; }
      p { margin: 0; color: var(--muted); line-height: 1.5; }
      a { color: var(--primary); text-decoration: none; }
      main {
        display: grid;
        grid-template-columns: minmax(400px, 480px) minmax(0, 1fr);
        gap: 18px;
        padding: 18px 24px 24px;
        height: calc(100vh - 78px);
        min-height: 640px;
        overflow: hidden;
      }
      .panel {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: 0 12px 30px rgba(16, 24, 40, .06);
      }
      .left {
        display: flex;
        flex-direction: column;
        min-height: 0;
        align-self: start;
        max-height: 100%;
        overflow: hidden;
      }
      .tabs {
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 16px 0;
      }
      .tab {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 10px;
        margin: 0;
        min-height: 42px;
        padding: 10px 12px;
        color: #d7deea;
        background: transparent;
        border-radius: 8px;
        text-align: left;
      }
      .tab:hover { background: rgba(255,255,255,.08); }
      .tab.active { color: #fff; background: #2563eb; }
      .tab-content {
        display: none;
        padding: 20px;
        overflow: auto;
      }
      .tab-content.active { display: block; flex: 1; min-height: 0; }
      .right {
        display: flex;
        flex-direction: column;
        min-width: 0;
        min-height: 0;
        max-height: 100%;
        overflow: hidden;
      }
      .right-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 16px 18px;
        border-bottom: 1px solid var(--line);
      }
      .toolbar { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
      .badge {
        display: inline-flex;
        align-items: center;
        min-height: 28px;
        padding: 4px 10px;
        border-radius: 999px;
        color: var(--ok);
        background: #e8f7f4;
        font-size: 13px;
      }
      .badge.neutral {
        color: #344054;
        background: #f2f4f7;
      }
      .section-kicker {
        margin-bottom: 14px;
        color: var(--muted);
        font-size: 13px;
      }
      label {
        display: block;
        margin-top: 12px;
        font-size: 13px;
        color: #344054;
      }
      .inline-check {
        display: flex;
        align-items: center;
        gap: 8px;
      }
      .inline-check input {
        width: auto;
        min-height: auto;
        margin: 0;
      }
      textarea, input, select {
        width: 100%;
        min-height: 40px;
        padding: 10px 12px;
        margin-top: 6px;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        font: inherit;
        color: var(--text);
        background: #fff;
        outline: none;
      }
      textarea { resize: vertical; }
      textarea:focus, input:focus, select:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(18, 100, 216, .12);
      }
      button {
        min-height: 40px;
        margin-top: 14px;
        padding: 10px 15px;
        border: 0;
        border-radius: 6px;
        background: var(--primary);
        color: #fff;
        font: inherit;
        cursor: pointer;
      }
      button:hover { background: var(--primary-dark); }
      button.secondary { background: #475467; }
      button.secondary:hover { background: #344054; }
      button.ghost {
        margin: 0;
        color: #344054;
        background: #f2f4f7;
      }
      button.ghost:hover { background: #e4e7ec; }
      button:disabled { cursor: not-allowed; opacity: .65; }
      .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
      .hint { margin-top: 10px; font-size: 13px; color: var(--muted); line-height: 1.5; }
      .form-card {
        padding: 14px;
        margin-top: 14px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #fbfcfe;
      }
      .quick { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
      .quick button {
        margin: 0;
        min-height: 32px;
        padding: 6px 10px;
        color: #344054;
        background: #f2f4f7;
      }
      .quick button:hover { background: #e4e7ec; }
      .output {
        flex: 1;
        min-height: 0;
        height: 100%;
        padding: 20px;
        background: #f8fafc;
        overflow: auto;
        border-radius: 0 0 8px 8px;
      }
      .empty, .loading {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 460px;
        color: var(--muted);
        text-align: center;
        line-height: 1.7;
      }
      .spinner {
        width: 18px;
        height: 18px;
        margin-right: 10px;
        border: 2px solid #cbd5e1;
        border-top-color: var(--primary);
        border-radius: 999px;
        animation: spin .8s linear infinite;
      }
      @keyframes spin { to { transform: rotate(360deg); } }
      .answer {
        white-space: pre-wrap;
        line-height: 1.75;
        padding: 18px;
        border-radius: 8px;
        background: #fff;
        border: 1px solid var(--line);
        margin-bottom: 18px;
        font-size: 15px;
      }
      .report {
        display: grid;
        gap: 16px;
      }
      .report-hero {
        padding: 18px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #fff;
      }
      .report-title {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
      }
      .report-title h3 { margin: 0; font-size: 17px; }
      .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 10px;
      }
      .metric-card {
        padding: 12px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #fff;
      }
      .metric-value { font-size: 22px; font-weight: 800; }
      .metric-label { margin-top: 2px; color: var(--muted); font-size: 12px; }
      .section-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        margin: 8px 0 0;
      }
      .section-title h3 { margin: 0; }
      .card-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
      }
      .result-item {
        padding: 12px;
        border: 1px solid var(--line);
        border-radius: 8px;
        margin-top: 10px;
        background: #fff;
        line-height: 1.6;
      }
      .result-item strong { display: block; margin-bottom: 6px; }
      .muted { color: var(--muted); font-size: 13px; }
      .error { color: var(--danger); white-space: pre-wrap; }
      .status-card {
        padding: 16px;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #fff;
      }
      .status-card h3 { margin-top: 0; }
      .pill {
        display: inline-flex;
        align-items: center;
        min-height: 24px;
        padding: 3px 8px;
        border-radius: 999px;
        color: #344054;
        background: #eef2f6;
        font-size: 12px;
      }
      .pill.ok { color: #067647; background: #dcfae6; }
      .pill.warn { color: #b54708; background: #fef0c7; }
      .action-row {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 10px;
      }
      .action-row button { margin-top: 0; }
      .chat-tools {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin-bottom: 10px;
      }
      .chat-input-row {
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 10px;
        align-items: end;
      }
      .memory-toggle {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 12px;
        color: #344054;
        font-size: 13px;
      }
      .memory-toggle input { width: auto; min-height: auto; margin: 0; }
      .chat-feed {
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      .chat-row {
        display: flex;
        flex-direction: column;
      }
      .chat-row.user { align-items: flex-end; }
      .chat-row.assistant { align-items: flex-start; }
      .chat-role {
        margin: 0 4px 4px;
        color: var(--muted);
        font-size: 12px;
      }
      .chat-bubble {
        max-width: 86%;
        padding: 12px 14px;
        border-radius: 8px;
        line-height: 1.7;
        white-space: pre-wrap;
      }
      .chat-bubble.user {
        align-self: flex-end;
        color: #fff;
        background: var(--primary);
      }
      .chat-bubble.assistant {
        align-self: flex-start;
        color: var(--text);
        background: #fff;
        border: 1px solid var(--line);
      }
      .chat-meta {
        align-self: flex-start;
        max-width: 86%;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.5;
      }
      @media (max-width: 1100px) {
        .app-shell { grid-template-columns: 1fr; }
        .sidebar { min-height: auto; }
        .tabs { flex-direction: row; flex-wrap: wrap; }
        .tab { flex: 1 1 calc(25% - 6px); }
        main { grid-template-columns: 1fr; height: auto; overflow: visible; }
        .right { max-height: none; overflow: visible; }
        .output { max-height: 70vh; }
      }
      @media (max-width: 720px) {
        .topbar { align-items: flex-start; flex-direction: column; padding: 16px; }
        main { padding: 16px; }
        .grid2 { grid-template-columns: 1fr; }
        .metric-grid, .card-grid { grid-template-columns: 1fr; }
        .tabs { overflow-x: auto; }
        .tab { flex: 1 1 calc(50% - 6px); }
      }
    </style>
  </head>
  <body>
    <div class="app-shell">
      <aside class="sidebar">
        <div class="brand">
          <div class="brand-mark">AI</div>
          <div>
            <div class="brand-title">运营智能体</div>
            <div class="brand-subtitle">产品知识库工作台</div>
          </div>
        </div>
        <div class="tabs">
          <button class="tab active" onclick="switchTab('chat')">对话问答</button>
          <button class="tab" onclick="switchTab('content')">热点创作</button>
          <button class="tab" onclick="switchTab('files')">资料中心</button>
          <button class="tab" onclick="switchTab('viral')">爆款案例</button>
          <button class="tab" onclick="switchTab('benchmark')">对标创作</button>
          <button class="tab" onclick="switchTab('history')">生成历史</button>
          <button class="tab" onclick="switchTab('product')">产品入库</button>
          <button class="tab" onclick="switchTab('memory')">长期记忆</button>
        </div>
        <div class="sidebar-foot">
          <div>本地知识库已连接</div>
          <div>接口文档：<a href="/docs">/docs</a></div>
        </div>
      </aside>

      <div class="workspace">
        <header class="topbar">
          <div>
            <h1>产品运营智能体</h1>
            <p>产品资料问答、热点内容创作、竞品案例沉淀和长期记忆。</p>
          </div>
          <div class="toolbar">
            <span class="badge">数据库在线</span>
            <span class="badge neutral">RAG 检索</span>
            <span class="badge neutral">联网搜索</span>
          </div>
        </header>

    <main>
      <section class="panel left">

        <div class="tab-content active" id="tab-chat">
          <h2>运营助手对话</h2>
          <div class="section-kicker">用于产品问答、客服话术、策略讨论和连续上下文对话。</div>
          <div class="chat-tools">
            <label>回答模式
              <select id="mode">
                <option value="qa">产品问答</option>
                <option value="assistant" selected>运营助手</option>
                <option value="customer_service">客服话术</option>
                <option value="script">内容脚本</option>
                <option value="campaign">活动策划</option>
              </select>
            </label>
            <label>参考资料数
              <select id="topK">
                <option value="4">4</option>
                <option value="6" selected>6</option>
                <option value="8">8</option>
                <option value="10">10</option>
              </select>
            </label>
            <label>资料来源模式
              <select id="sourceMode">
                <option value="knowledge_only">只查我的知识库</option>
                <option value="llm_only">通用大模型回答</option>
                <option value="knowledge_llm" selected>知识库 + 大模型</option>
                <option value="web_knowledge_llm">知识库 + 联网搜索 + 大模型</option>
              </select>
            </label>
          </div>
          <label class="memory-toggle"><input id="autoMemory" type="checkbox" checked> 自动总结有价值对话，写入长期记忆</label>
          <div class="quick">
            <button type="button" onclick="fillQuestion('6个月以下能不能吃牛初乳？', 'qa')">牛初乳用法</button>
            <button type="button" onclick="fillQuestion('根据高频咨询标准问答库，帮我整理客服回复话术', 'customer_service')">客服话术</button>
            <button type="button" onclick="fillQuestion('请根据知识库介绍一下目前有哪些产品资料', 'qa')">资料概览</button>
          </div>
          <label>输入消息<textarea id="q" rows="5" placeholder="像和运营同事聊天一样输入：帮我基于牛初乳产品做一套直播间转化话术"></textarea></label>
          <div class="chat-input-row">
            <button id="clearChatBtn" class="secondary" onclick="clearChat()">清空本轮对话</button>
            <button id="askBtn" onclick="ask()">发送</button>
          </div>
        </div>

        <div class="tab-content" id="tab-content">
          <h2>内容创作工作台</h2>
          <div class="section-kicker">联网搜索公开线索，并结合知识库、记忆和案例生成脚本/图文/SEO方案。</div>
          <label>产品/主题<input id="wfProduct"></label>
          <div class="grid2">
            <label>平台
              <select id="wfPlatform">
                <option value="抖音">抖音</option>
                <option value="快手">快手</option>
                <option value="小红书">小红书</option>
                <option value="百度">百度</option>
                <option value="公众号">公众号</option>
                <option value="知乎">知乎</option>
              </select>
            </label>
            <label>创作模块
              <select id="wfModule">
                <option value="short_video">短视频脚本</option>
                <option value="seo_article">SEO搜索图文</option>
                <option value="product_photo_post">产品实拍图文</option>
                <option value="caption_copy">字幕/口播文案</option>
                <option value="recommendation_post">推荐种草方向</option>
                <option value="viral_format_mimic">爆款格式模仿</option>
              </select>
            </label>
          </div>
          <div class="grid2">
            <label>目标
              <select id="wfGoal">
                <option value="种草转化">种草转化</option>
                <option value="活动预热">活动预热</option>
                <option value="直播引流">直播引流</option>
                <option value="客服答疑">客服答疑</option>
                <option value="SEO获客">SEO获客</option>
                <option value="推荐流量">推荐流量</option>
              </select>
            </label>
            <label>目标人群<input id="wfAudience"></label>
          </div>
          <label>关键词/SEO词<input id="wfKeywords" placeholder="例如：牛初乳怎么吃、宝宝营养补充、送礼香氛礼盒"></label>
          <label>SEO搜索方向<textarea id="wfSeoGoal" rows="3" placeholder="例如：围绕用户会搜索的问题做标题矩阵和FAQ，兼顾百度/小红书搜索收录"></textarea></label>
          <label>产品实拍/配图要求<textarea id="wfImageRequirements" rows="3" placeholder="例如：产品实拍、包装细节、使用场景、字幕压图、首图要有痛点标题"></textarea></label>
          <label>参考/模仿格式<textarea id="wfReferenceStyle" rows="3" placeholder="例如：模仿市面爆款的开头结构、封面标题、图文排版、推荐理由顺序"></textarea></label>
          <label>额外要求<textarea id="wfExtra" rows="4"></textarea></label>
          <button id="contentBtn" onclick="createContent()">联网生成内容方案</button>
          <div class="hint">会搜索公开网页热点线索，并结合产品知识库、长期记忆和爆款案例生成图文/脚本/SEO方案。</div>
        </div>
        <div class="tab-content" id="tab-files">
          <h2>资料中心</h2>
          <div class="section-kicker">上传文件、分析资料，或把文件夹批量向量化写入知识库。</div>
          <label>上传文件
            <input id="docFile" type="file" accept=".txt,.md,.csv,.xlsx,.xls,.pdf">
          </label>
          <label>分析指令<textarea id="fileInstruction" rows="3">请分析这个文件的核心内容、可用于产品运营的要点和需要注意的风险。</textarea></label>
          <div class="grid2">
            <button id="uploadBtn" onclick="uploadDocument()">上传并向量化入库</button>
            <button id="analyzeBtn" class="secondary" onclick="analyzeDocument()">只分析文件</button>
          </div>
          <h3>批量导入文件夹</h3>
          <label>本地文件夹路径<input id="folderPath" value="E:\ai-agent\uploads\产品资料"></label>
          <label class="inline-check"><input id="resetBeforeIngest" type="checkbox"> 导入前清空现有知识库</label>
          <div class="grid2">
            <button id="folderBtn" onclick="ingestFolder()">导入文件夹并向量化</button>
            <button id="folderAnalyzeBtn" class="secondary" onclick="analyzeFolder()">只分析文件夹</button>
          </div>
          <div class="hint">支持 txt、md、csv、xlsx、xls、pdf。PDF 解析需要安装 pypdf。</div>
        </div>

        <div class="tab-content" id="tab-viral">
          <h2>爆款/竞品案例投喂</h2>
          <div class="section-kicker">把发布表现好、结构值得复用的内容沉淀为案例库。</div>
          <div class="grid2">
            <label>平台<input id="casePlatform" placeholder="抖音 / 快手 / 小红书"></label>
            <label>产品/类目<input id="caseProduct" placeholder="牛初乳 / 香氛礼盒"></label>
          </div>
          <label>标题<input id="caseTitle" placeholder="爆款视频标题或选题"></label>
          <label>链接<input id="caseUrl" placeholder="可粘贴视频链接、竞品页面或素材地址"></label>
          <label>作者/账号<input id="caseAuthor" placeholder="竞品账号或达人名称"></label>
          <label>数据指标 JSON<textarea id="caseMetrics" rows="3" placeholder='例如 {"点赞":12000,"评论":860,"收藏":2300}'></textarea></label>
          <label>文案/脚本/评论摘要<textarea id="caseContent" rows="6" placeholder="粘贴爆款视频文案、脚本、评论高频问题或你的观察"></textarea></label>
          <label>标签<input id="caseTags" placeholder="钩子强 / 情绪价值 / 价格锚点 / 送礼场景"></label>
          <div class="grid2">
            <button id="caseBtn" onclick="saveViralCase()">保存并拆解案例</button>
            <button class="secondary" onclick="loadViralCases()">查看案例库</button>
          </div>
          <div class="hint">保存后会自动拆解爆款结构，并写入知识库；后续热点脚本创作会优先参考这些案例。</div>
        </div>

        <div class="tab-content" id="tab-benchmark">
          <h2>对标图文创作</h2>
          <div class="section-kicker">粘贴或上传对标作品，拆解其结构后生成适合你产品的原创版本。</div>
          <div class="grid2">
            <label>平台
              <select id="benchmarkPlatform">
                <option value="小红书">小红书</option>
                <option value="抖音图文">抖音图文</option>
                <option value="快手图文">快手图文</option>
                <option value="公众号">公众号</option>
                <option value="百度SEO">百度SEO</option>
              </select>
            </label>
            <label>产品/主题<input id="benchmarkProduct" placeholder="例如：牛初乳、香氛礼盒、生命阳光某产品"></label>
          </div>
          <div class="grid2">
            <label>目标人群<input id="benchmarkAudience" placeholder="例如：宝妈、送礼人群、20-35岁女性"></label>
            <label>关键词/SEO词<input id="benchmarkKeywords" placeholder="例如：宝宝营养、520礼物、送礼推荐"></label>
          </div>
          <label>上传对标文件
            <input id="benchmarkFile" type="file" accept=".txt,.md,.csv,.xlsx,.xls,.pdf,.png,.jpg,.jpeg,.webp,.gif">
          </label>
          <label>对标内容/拆解备注<textarea id="benchmarkText" rows="6" placeholder="粘贴对标图文的标题、正文、封面字、图片顺序、评论区亮点，或写清楚你想模仿它的哪一点。纯图片请在这里补充画面和文字描述。"></textarea></label>
          <label>我的创作需求<textarea id="benchmarkRequirement" rows="4" placeholder="例如：模仿这个爆款图文结构，为我的产品生成一篇小红书种草图文，语气自然，不夸大功效，适合投流前测试。"></textarea></label>
          <button id="benchmarkBtn" onclick="createBenchmarkContent()">按对标作品生成</button>
          <div class="hint">这个模块用于“学习结构，不照搬内容”。当前可解析文本、PDF、Excel；图片会先记录文件名，需要你补充画面/文字描述，后续可接多模态视觉模型自动读图。</div>
        </div>

        <div class="tab-content" id="tab-history">
          <h2>生成历史</h2>
          <div class="section-kicker">查看历史生成内容，把发布后表现好的内容转为爆款案例。</div>
          <button id="historyBtn" onclick="loadGenerationHistory()">刷新生成历史</button>
          <div class="hint">热点创作和对标创作会自动保存到这里。内容发布后，如果数据表现不错，可以补充链接和数据，一键转为爆款案例库。</div>
          <label>转案例数据填写说明<textarea rows="4" readonly>点击某条历史的“转为爆款案例”，按提示填写标题、发布链接、数据指标和复盘标签。数据指标可以写 JSON，例如 {"播放":120000,"点赞":8600,"评论":430,"收藏":1200}。</textarea></label>
        </div>

        <div class="tab-content" id="tab-product">
          <h2>添加产品资料</h2>
          <div class="section-kicker">临时补充单个产品资料，保存后会自动写入向量知识库。</div>
          <label>产品名称<input id="productName"></label>
          <label>产品类目<input id="category"></label>
          <label>目标人群<input id="audience"></label>
          <label>核心卖点<textarea id="sellingPoints" rows="3"></textarea></label>
          <label>宣传注意事项<textarea id="cautions" rows="2"></textarea></label>
          <label>补充知识<textarea id="knowledgeText" rows="4"></textarea></label>
          <button onclick="createProduct()">保存产品并入库</button>
          <div class="hint">适合临时补充单个产品。批量资料建议继续用导入脚本。</div>
        </div>

        <div class="tab-content" id="tab-memory">
          <h2>长期记忆</h2>
          <div class="section-kicker">保存品牌规则、表达偏好、禁用话术和复盘经验。</div>
          <label>记忆内容<textarea id="memoryContent" rows="5"></textarea></label>
          <button class="secondary" onclick="saveMemory()">保存记忆</button>
          <div class="hint">适合保存你的回答偏好、品牌规则、禁用表达和活动复盘。</div>
        </div>
      </section>

      <section class="panel right">
        <div class="right-head">
          <div>
            <h2>结果输出</h2>
            <p id="statusText">等待任务</p>
          </div>
          <div class="toolbar">
            <button class="ghost" onclick="loadCounts()">查看数据量</button>
            <button class="ghost" onclick="restoreLastResult()">返回上次答案</button>
          </div>
        </div>
        <div class="output" id="out"><div class="empty">我是你的产品运营助手。你可以连续对话，我会参考本轮上下文、长期记忆和产品知识库回答。</div></div>
      </section>
    </main>
      </div>
    </div>

    <script>
      let lastResultHtml = '';
      let lastBusinessResultHtml = '';
      let chatMessages = [];

      function setStatus(text) {
        document.getElementById('statusText').textContent = text;
      }

      function switchTab(name) {
        document.querySelectorAll('.tab').forEach((el) => el.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach((el) => el.classList.remove('active'));
        const tabs = ['chat', 'content', 'files', 'viral', 'benchmark', 'history', 'product', 'memory'];
        const index = tabs.indexOf(name);
        document.querySelectorAll('.tab')[index].classList.add('active');
        document.getElementById(`tab-${name}`).classList.add('active');
      }

      function setLoading(text, buttonId) {
        setStatus(text);
        document.getElementById('out').innerHTML = `<div class="loading"><span class="spinner"></span>${escapeHtml(text)}</div>`;
        if (buttonId) {
          const button = document.getElementById(buttonId);
          button.dataset.originalText = button.dataset.originalText || button.textContent;
          button.textContent = '处理中...';
          button.disabled = true;
        }
      }

      function stopLoading(buttonId, status) {
        if (buttonId) {
          const button = document.getElementById(buttonId);
          button.disabled = false;
          if (button.dataset.originalText) button.textContent = button.dataset.originalText;
        }
        setStatus(status || '已完成');
      }

      function saveResult(html) {
        lastResultHtml = html;
        lastBusinessResultHtml = html;
        document.getElementById('out').innerHTML = html;
      }

      async function copyAnswer() {
        const answer = document.querySelector('#out .answer');
        if (!answer) {
          setStatus('当前没有可复制的答案');
          return;
        }
        await navigator.clipboard.writeText(answer.textContent || '');
        setStatus('答案已复制');
      }

      function metricCard(value, label) {
        return `<div class="metric-card"><div class="metric-value">${escapeHtml(value)}</div><div class="metric-label">${escapeHtml(label)}</div></div>`;
      }

      function renderChat() {
        if (!chatMessages.length) {
          document.getElementById('out').innerHTML = '<div class="empty">我是你的产品运营助手。你可以连续对话，我会参考本轮上下文、长期记忆和产品知识库回答。</div>';
          return;
        }
        document.getElementById('out').innerHTML = `
          <div class="chat-feed">
            ${chatMessages.map((item) => `
              <div class="chat-row ${item.role}">
                <div class="chat-role">${item.role === 'user' ? '你' : '运营助手'}</div>
                <div class="chat-bubble ${item.role}">${displayText(item.content)}</div>
                ${item.meta ? `<div class="chat-meta">${displayText(item.meta)}</div>` : ''}
              </div>
            `).join('')}
          </div>
        `;
        document.getElementById('out').scrollTop = document.getElementById('out').scrollHeight;
        lastResultHtml = document.getElementById('out').innerHTML;
        lastBusinessResultHtml = lastResultHtml;
      }

      function clearChat() {
        chatMessages = [];
        renderChat();
        setStatus('本轮对话已清空，长期记忆不受影响');
      }

      function restoreLastResult() {
        if (lastBusinessResultHtml) {
          document.getElementById('out').innerHTML = lastBusinessResultHtml;
          setStatus('已返回上次答案');
        } else if (chatMessages.length) {
          renderChat();
          setStatus('已返回对话');
        } else {
          setStatus('暂无可返回的答案');
        }
      }

      function show(data) {
        const html = `<div class="status-card"><pre>${escapeHtml(JSON.stringify(data, null, 2))}</pre></div>`;
        saveResult(html);
      }

      function escapeHtml(value) {
        return String(value ?? '')
          .replaceAll('&', '&amp;')
          .replaceAll('<', '&lt;')
          .replaceAll('>', '&gt;')
          .replaceAll('"', '&quot;')
          .replaceAll("'", '&#039;');
      }

      function cleanDisplayText(value) {
        return String(value ?? '')
          .replace(/```[\s\S]*?```/g, (block) => block.replaceAll('```', ''))
          .replace(/\*\*/g, '')
          .replace(/\*/g, '')
          .replace(/^#{1,6}\s*/gm, '')
          .replace(/^\s*[-–]\s+/gm, '· ');
      }

      function displayText(value) {
        return escapeHtml(cleanDisplayText(value));
      }


      function sourceModeLabel(value) {
        const labels = {
          knowledge_only: '只查我的知识库',
          llm_only: '通用大模型回答',
          knowledge_llm: '知识库 + 大模型',
          web_knowledge_llm: '知识库 + 联网搜索 + 大模型'
        };
        return labels[value] || '知识库 + 大模型';
      }
      function showChat(data) {
        const retrieved = data.retrieved || [];
        const memories = data.memories || [];
        const meta = [
          `资料来源：${sourceModeLabel(data.source_mode)}`,
          data.web_results && data.web_results.length ? `联网线索：${data.web_results.length} 条` : '',
          `参考资料：${retrieved.length} 条`,
          `读取长期记忆：${memories.length} 条`,
          data.auto_memory_saved ? `已自动写入长期记忆：${data.auto_memory}` : ''
        ].filter(Boolean).join(' | ');
        chatMessages.push({ role: 'assistant', content: data.answer || '', meta });
        renderChat();
        return;
        const html = `
          <div class="answer">${displayText(data.answer || '')}</div>
          <h3>参考资料</h3>
          ${retrieved.length ? retrieved.map((item, index) => `
            <div class="result-item">
              <strong>资料 ${index + 1} <span class="muted">相关度：${Number(item.score || 0).toFixed(3)}</span></strong>
              <div class="muted">来源：${escapeHtml(item.source || '知识库')}</div>
              <div>${displayText(item.content)}</div>
            </div>
          `).join('') : '<div class="muted">没有检索到参考资料。</div>'}
          <h3>长期记忆</h3>
          ${memories.length ? memories.map((item) => `<div class="result-item">${displayText(item)}</div>`).join('') : '<div class="muted">暂无长期记忆。</div>'}
        `;
        saveResult(html);
      }

      function showContentWorkflow(data) {
        const trends = data.trends || [];
        const retrieved = data.retrieved || [];
        const diagnostics = data.search_diagnostics || [];
        const viralCases = data.viral_cases || [];
        const successCount = diagnostics.filter((item) => item.ok).length;
        const totalResultCount = diagnostics.reduce((sum, item) => sum + Number(item.count || 0), 0);
        const sourceSummary = totalResultCount > 0
          ? `联网状态：成功，公开搜索返回 ${totalResultCount} 条线索。本次生成已结合公开搜索、产品知识库、长期记忆和案例库。`
          : '联网状态：失败或无结果。本次生成主要来自大模型、产品知识库、长期记忆和通用内容结构，未使用真实公开搜索线索。';
        const html = `
          <div class="report">
            <div class="report-hero">
              <div class="report-title">
                <div>
                  <h3>内容方案</h3>
                  <p>${escapeHtml(sourceSummary)}</p>
                </div>
                <span class="pill ${totalResultCount > 0 ? 'ok' : 'warn'}">${totalResultCount > 0 ? '联网成功' : '未使用联网线索'}</span>
              </div>
              <div class="metric-grid">
                ${metricCard(String(totalResultCount), '公开搜索线索')}
                ${metricCard(`${successCount}/${diagnostics.length}`, '成功搜索组')}
                ${metricCard(String(retrieved.length), '产品资料引用')}
                ${metricCard(String(viralCases.length), '案例引用')}
              </div>
              <div class="action-row">
                <button class="secondary" onclick="copyAnswer()">复制方案</button>
                ${data.history_id ? `<button class="secondary" onclick="loadGenerationHistory()">查看生成历史</button>` : ''}
              </div>
            </div>
            <div class="answer">${displayText(data.answer || '')}</div>
            <div class="section-title"><h3>搜索状态</h3><span class="pill">诊断</span></div>
            <div class="card-grid">
              ${diagnostics.length ? diagnostics.map((item) => `
                <div class="result-item">
                  <strong>${item.ok ? '已获取' : '未获取'}：${escapeHtml(item.query || '')}</strong>
                  <div class="muted">结果数：${item.count || 0} / 搜索源：${escapeHtml(item.provider || '公开搜索')}</div>
                  ${item.reason ? `<div class="muted">说明：${escapeHtml(item.reason)}</div>` : ''}
                </div>
              `).join('') : '<div class="muted">暂无搜索诊断。</div>'}
            </div>
            <div class="section-title"><h3>搜索线索</h3><span class="pill">${trends.length} 条</span></div>
            <div class="card-grid">
              ${trends.length ? trends.map((item, index) => `
                <div class="result-item">
                  <strong>线索 ${index + 1}：${escapeHtml(item.title || '')}</strong>
                  <div class="muted">${escapeHtml(item.snippet || '')}</div>
                  <div class="muted">${escapeHtml(item.url || '')}</div>
                </div>
              `).join('') : '<div class="muted">没有检索到公开热点线索，已按通用爆款结构生成。</div>'}
            </div>
            <div class="section-title"><h3>参考爆款/竞品案例</h3><span class="pill">${viralCases.length} 条</span></div>
            ${viralCases.length ? viralCases.map((item, index) => `
              <div class="result-item">
                <strong>案例 ${index + 1}：${escapeHtml(item.title || '未命名案例')}</strong>
                <div class="muted">${escapeHtml(item.platform || '')} / ${escapeHtml(item.product || '')}</div>
                <div>${displayText((item.analysis || item.content || '').slice(0, 700))}</div>
              </div>
            `).join('') : '<div class="muted">暂无匹配的手动爆款/竞品案例。</div>'}
            <div class="section-title"><h3>产品资料引用</h3><span class="pill">${retrieved.length} 条</span></div>
            ${retrieved.length ? retrieved.map((item, index) => `
              <div class="result-item">
                <strong>资料 ${index + 1} <span class="muted">相关度：${Number(item.score || 0).toFixed(3)}</span></strong>
                <div class="muted">来源：${escapeHtml(item.source || '知识库')}</div>
                <div>${displayText(item.content)}</div>
              </div>
            `).join('') : '<div class="muted">没有检索到产品资料。</div>'}
          </div>
        `;
        saveResult(html);
      }
      function showBenchmarkWorkflow(data) {
        const retrieved = data.retrieved || [];
        const parsedSources = data.parsed_sources || [];
        const html = `
          <div class="report">
            <div class="report-hero">
              <div class="report-title">
                <div>
                  <h3>对标创作方案</h3>
                  <p>已结合对标资料、产品知识和长期记忆生成原创版本。</p>
                </div>
                <span class="pill ok">已生成</span>
              </div>
              <div class="metric-grid">
                ${metricCard(String(parsedSources.length), '对标资料')}
                ${metricCard(String(retrieved.length), '产品资料引用')}
                ${metricCard(data.image_note ? '需补充' : '正常', '图片解析状态')}
                ${metricCard(data.history_id ? '已保存' : '未保存', '生成历史')}
              </div>
              <div class="action-row">
                <button class="secondary" onclick="copyAnswer()">复制方案</button>
                ${data.history_id ? `<button class="secondary" onclick="loadGenerationHistory()">查看生成历史</button>` : ''}
              </div>
            </div>
            <div class="answer">${displayText(data.answer || '')}</div>
            ${data.image_note ? `<div class="status-card"><h3>图片提示</h3><p>${escapeHtml(data.image_note)}</p></div>` : ''}
            <div class="section-title"><h3>对标资料</h3><span class="pill">${parsedSources.length} 条</span></div>
            <div class="card-grid">
              ${parsedSources.length ? parsedSources.map((item, index) => `
                <div class="result-item">
                  <strong>资料 ${index + 1}：${escapeHtml(item.source || '对标资料')}</strong>
                  <div class="muted">类型：${escapeHtml(item.type || '')} / 已读取字符：${item.chars || 0}</div>
                </div>
              `).join('') : '<div class="muted">本次未读取到可解析的对标文本。</div>'}
            </div>
            <div class="section-title"><h3>产品知识引用</h3><span class="pill">${retrieved.length} 条</span></div>
            ${retrieved.length ? retrieved.map((item, index) => `
              <div class="result-item">
                <strong>资料 ${index + 1} <span class="muted">相关度：${Number(item.score || 0).toFixed(3)}</span></strong>
                <div class="muted">来源：${escapeHtml(item.source || '知识库')}</div>
                <div>${displayText(item.content)}</div>
              </div>
            `).join('') : '<div class="muted">没有检索到产品资料，建议先导入产品资料后再生成。</div>'}
          </div>
        `;
        saveResult(html);
      }

      function showIngestResult(data) {
        const files = data.files || data.documents || [];
        const html = `
          <div class="status-card">
            <h3>资料处理完成</h3>
            <p>成功入库：${data.count ?? files.length} 份文档</p>
          </div>
          ${files.length ? files.map((item, index) => `
            <div class="result-item">
              <strong>文件 ${index + 1}</strong>
              <div>${escapeHtml(item.title || item.file || item.filename || '')}</div>
              ${item.error ? `<div class="error">${escapeHtml(item.error)}</div>` : '<div class="muted">已写入知识库并完成向量化。</div>'}
            </div>
          `).join('') : ''}
        `;
        saveResult(html);
      }

      function showError(err) {
        saveResult(`<div class="error">操作失败：${escapeHtml(JSON.stringify(err, null, 2))}</div>`);
        setStatus('任务失败');
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

      async function requestForm(url, formData) {
        const res = await fetch(url, { method: 'POST', body: formData });
        const data = await res.json();
        if (!res.ok) throw data;
        return data;
      }

      async function createProduct() {
        try {
          setLoading('正在保存产品资料...', null);
          const data = await requestJson('/products', {
            name: document.getElementById('productName').value,
            category: document.getElementById('category').value,
            target_audience: document.getElementById('audience').value,
            selling_points: document.getElementById('sellingPoints').value,
            cautions: document.getElementById('cautions').value,
            knowledge_text: document.getElementById('knowledgeText').value
          });
          saveResult(`<div class="status-card">产品已保存并入库：${escapeHtml(data.name)}</div>`);
          stopLoading(null, '产品已入库');
        } catch (err) {
          showError(err);
        }
      }

      async function saveMemory() {
        try {
          setLoading('正在保存长期记忆...', null);
          await requestJson('/memories', {
            memory_type: 'user_preference',
            content: document.getElementById('memoryContent').value,
            importance: 4
          });
          saveResult('<div class="status-card">长期记忆已保存。</div>');
          stopLoading(null, '记忆已保存');
        } catch (err) {
          showError(err);
        }
      }

      async function ask() {
        try {
          const message = document.getElementById('q').value.trim();
          if (!message) return;
          const history = chatMessages.slice(-12);
          chatMessages.push({ role: 'user', content: message });
          renderChat();
          document.getElementById('q').value = '';
          setStatus('正在结合上下文、长期记忆和知识库生成回答...');
          const askButton = document.getElementById('askBtn');
          askButton.dataset.originalText = askButton.dataset.originalText || askButton.textContent;
          askButton.textContent = '思考中...';
          askButton.disabled = true;
          const data = await requestJson('/chat', {
            message,
            session_id: 'browser',
            mode: document.getElementById('mode').value,
            source_mode: document.getElementById('sourceMode').value,
            top_k: Number(document.getElementById('topK').value),
            history,
            auto_memory: document.getElementById('autoMemory').checked
          });
          showChat(data);
          stopLoading('askBtn', '回答已生成');
        } catch (err) {
          stopLoading('askBtn', '任务失败');
          chatMessages.push({ role: 'assistant', content: `操作失败：${JSON.stringify(err, null, 2)}` });
          renderChat();
        }
      }

      async function createContent() {
        try {
          setLoading('正在联网搜索热点并生成脚本方案...', 'contentBtn');
          const data = await requestJson('/workflows/content', {
            product: document.getElementById('wfProduct').value,
            platform: document.getElementById('wfPlatform').value,
            goal: document.getElementById('wfGoal').value,
            audience: document.getElementById('wfAudience').value,
            content_module: document.getElementById('wfModule').value,
            keywords: document.getElementById('wfKeywords').value,
            seo_goal: document.getElementById('wfSeoGoal').value,
            image_requirements: document.getElementById('wfImageRequirements').value,
            reference_style: document.getElementById('wfReferenceStyle').value,
            extra_requirements: document.getElementById('wfExtra').value,
            top_k: 6,
            search_limit: 4
          });
          showContentWorkflow(data);
          stopLoading('contentBtn', '脚本方案已生成');
        } catch (err) {
          stopLoading('contentBtn', '任务失败');
          showError(err);
        }
      }
      async function createBenchmarkContent() {
        try {
          const file = document.getElementById('benchmarkFile').files[0];
          const referenceText = document.getElementById('benchmarkText').value.trim();
          const requirement = document.getElementById('benchmarkRequirement').value.trim();
          if (!file && !referenceText) {
            saveResult('<div class="error">请先上传对标文件，或粘贴对标图文的标题、正文、结构和亮点。</div>');
            return;
          }
          setLoading('正在拆解对标作品并生成原创图文方案...', 'benchmarkBtn');
          const formData = new FormData();
          if (file) formData.append('file', file);
          formData.append('reference_text', referenceText);
          formData.append('product', document.getElementById('benchmarkProduct').value);
          formData.append('platform', document.getElementById('benchmarkPlatform').value);
          formData.append('audience', document.getElementById('benchmarkAudience').value);
          formData.append('keywords', document.getElementById('benchmarkKeywords').value);
          formData.append('requirement', requirement);
          const data = await requestForm('/workflows/benchmark', formData);
          showBenchmarkWorkflow(data);
          stopLoading('benchmarkBtn', '对标图文方案已生成');
        } catch (err) {
          stopLoading('benchmarkBtn', '任务失败');
          showError(err);
        }
      }

      function parseJsonOrRaw(value) {
        const raw = String(value || '').trim();
        if (!raw) return {};
        try {
          return JSON.parse(raw);
        } catch {
          return { raw };
        }
      }

      async function loadGenerationHistory() {
        try {
          switchTab('history');
          setLoading('正在读取生成历史...', 'historyBtn');
          const res = await fetch('/generation-history');
          const items = await res.json();
          const html = `
            <div class="report">
              <div class="report-hero">
                <div class="report-title">
                  <div>
                    <h3>生成历史</h3>
                    <p>共显示 ${items.length} 条最近生成记录。发布后表现好的内容可以转入案例库。</p>
                  </div>
                  <span class="pill">${items.length} 条</span>
                </div>
              </div>
              <div class="card-grid">
                ${items.length ? items.map((item, index) => `
                  <div class="result-item">
                    <strong>${index + 1}. ${escapeHtml(item.platform || '')} ${escapeHtml(item.product || '')} ${escapeHtml(item.goal || item.content_module || '')}</strong>
                    <div class="muted">类型：${escapeHtml(item.workflow || '')} / 模块：${escapeHtml(item.content_module || '')}</div>
                    <div class="muted">状态：${escapeHtml(item.status || '')} / 时间：${escapeHtml(item.created_at || '')}</div>
                    <div>${displayText((item.output_content || '').slice(0, 520))}</div>
                    <div class="action-row">
                      <button class="secondary" onclick="showHistoryDetail('${item.id}')">查看完整内容</button>
                      ${item.status === 'converted'
                        ? `<button class="secondary" disabled>已转案例</button>`
                        : `<button onclick="convertHistoryToCase('${item.id}')">转为爆款案例</button>`}
                      <button class="secondary" onclick="deleteGenerationHistory('${item.id}')">删除</button>
                    </div>
                  </div>
                `).join('') : '<div class="muted">还没有生成历史。先去“热点创作”或“对标创作”生成一次内容。</div>'}
              </div>
            </div>
          `;
          saveResult(html);
          window.__generationHistory = items;
          stopLoading('historyBtn', '历史已刷新');
        } catch (err) {
          stopLoading('historyBtn', '任务失败');
          showError(err);
        }
      }

      function showHistoryDetail(id) {
        const item = (window.__generationHistory || []).find((row) => row.id === id);
        if (!item) return;
        const html = `
          <div class="report">
            <div class="report-hero">
              <div class="report-title">
                <div>
                  <h3>生成记录详情</h3>
                  <p>${escapeHtml(item.platform || '')} / ${escapeHtml(item.product || '')} / ${escapeHtml(item.content_module || '')}</p>
                </div>
                <span class="pill">${escapeHtml(item.status || '')}</span>
              </div>
              <div class="action-row">
                <button class="secondary" onclick="copyAnswer()">复制内容</button>
                <button class="secondary" onclick="loadGenerationHistory()">返回生成历史</button>
              </div>
            </div>
            <div class="answer">${displayText(item.output_content || '')}</div>
            <div class="section-title"><h3>生成来源</h3><span class="pill">JSON</span></div>
            <div class="result-item">${displayText(JSON.stringify(item.source_summary || {}, null, 2))}</div>
          </div>
        `;
        saveResult(html);
      }

      async function convertHistoryToCase(id) {
        try {
          const item = (window.__generationHistory || []).find((row) => row.id === id) || {};
          const title = prompt('案例标题', `${item.platform || ''} ${item.product || ''} ${item.goal || item.content_module || ''}`.trim());
          if (title === null) return;
          const url = prompt('发布链接（可空）', '');
          if (url === null) return;
          const metricsRaw = prompt('数据指标 JSON（可空）', '{"播放":0,"点赞":0,"评论":0,"收藏":0}');
          if (metricsRaw === null) return;
          const tags = prompt('标签/复盘结论（可空）', '已发布脚本, 待复盘');
          if (tags === null) return;
          const notes = prompt('补充说明：为什么值得入库？（可空）', '');
          if (notes === null) return;
          setLoading('正在转为爆款案例并写入知识库...', null);
          const data = await requestJson(`/generation-history/${id}/to-case`, {
            title,
            url,
            metrics: parseJsonOrRaw(metricsRaw),
            tags,
            notes
          });
          const html = `
            <div class="status-card">
              <h3>已转为爆款案例</h3>
              <p>标题：${escapeHtml(data.title || '')}</p>
              <p>案例 ID：${escapeHtml(data.id || '')}</p>
            </div>
            <h3>案例拆解</h3>
            <div class="answer">${displayText(data.analysis || '')}</div>
          `;
          saveResult(html);
          stopLoading(null, '案例已入库');
        } catch (err) {
          stopLoading(null, '任务失败');
          showError(err);
        }
      }

      async function deleteGenerationHistory(id) {
        try {
          if (!confirm('确定删除这条生成历史吗？已经转为案例的内容不会删除案例库。')) return;
          setLoading('正在删除生成历史...', null);
          const res = await fetch(`/generation-history/${id}`, { method: 'DELETE' });
          const data = await res.json();
          if (!res.ok) throw data;
          stopLoading(null, '历史已删除');
          await loadGenerationHistory();
        } catch (err) {
          stopLoading(null, '任务失败');
          showError(err);
        }
      }

      function parseMetrics() {
        const raw = document.getElementById('caseMetrics').value.trim();
        if (!raw) return {};
        try {
          return JSON.parse(raw);
        } catch {
          return { raw };
        }
      }

      async function saveViralCase() {
        try {
          const content = document.getElementById('caseContent').value.trim();
          if (!content) {
            saveResult('<div class="error">请先粘贴文案、脚本或评论摘要。</div>');
            return;
          }
          setLoading('正在保存并拆解爆款案例...', 'caseBtn');
          const data = await requestJson('/viral-cases', {
            platform: document.getElementById('casePlatform').value,
            product: document.getElementById('caseProduct').value,
            title: document.getElementById('caseTitle').value,
            url: document.getElementById('caseUrl').value,
            author: document.getElementById('caseAuthor').value,
            metrics: parseMetrics(),
            content,
            tags: document.getElementById('caseTags').value
          });
          const html = `
            <div class="status-card">
              <h3>案例已保存</h3>
              <p>平台：${escapeHtml(data.platform || '')}</p>
              <p>产品/类目：${escapeHtml(data.product || '')}</p>
              <p>标题：${escapeHtml(data.title || '')}</p>
            </div>
            <h3>自动拆解</h3>
            <div class="answer">${displayText(data.analysis || '')}</div>
          `;
          saveResult(html);
          stopLoading('caseBtn', '爆款案例已入库');
        } catch (err) {
          stopLoading('caseBtn', '任务失败');
          showError(err);
        }
      }

      async function loadViralCases() {
        try {
          const res = await fetch('/viral-cases');
          const cases = await res.json();
          const html = `
            <div class="status-card"><h3>爆款/竞品案例库</h3><p>共显示 ${cases.length} 条最近案例</p></div>
            ${cases.map((item, index) => `
              <div class="result-item">
                <strong>${index + 1}. ${escapeHtml(item.title || '未命名案例')}</strong>
                <div class="muted">${escapeHtml(item.platform || '')} / ${escapeHtml(item.product || '')} / ${escapeHtml(item.author || '')}</div>
                <div>${displayText((item.content || '').slice(0, 500))}</div>
                <div class="muted">${escapeHtml(item.url || '')}</div>
              </div>
            `).join('')}
          `;
          saveResult(html);
          setStatus('已显示案例库');
        } catch (err) {
          showError(err);
        }
      }

      async function uploadDocument() {
        try {
          const file = document.getElementById('docFile').files[0];
          if (!file) {
            saveResult('<div class="error">请先选择一个文件。</div>');
            return;
          }
          setLoading('正在解析文件、切片并写入向量库...', 'uploadBtn');
          const formData = new FormData();
          formData.append('file', file);
          const data = await requestForm('/documents/upload', formData);
          showIngestResult(data);
          stopLoading('uploadBtn', '文件已入库');
        } catch (err) {
          stopLoading('uploadBtn', '任务失败');
          showError(err);
        }
      }

      async function analyzeDocument() {
        try {
          const file = document.getElementById('docFile').files[0];
          if (!file) {
            saveResult('<div class="error">请先选择一个文件。</div>');
            return;
          }
          setLoading('正在读取文件并调用大模型分析...', 'analyzeBtn');
          const formData = new FormData();
          formData.append('file', file);
          formData.append('instruction', document.getElementById('fileInstruction').value);
          const data = await requestForm('/documents/analyze-upload', formData);
          const html = `
            <div class="answer">${displayText(data.answer || '')}</div>
            <h3>文件预览</h3>
            ${(data.preview_documents || []).map((item, index) => `
              <div class="result-item">
                <strong>片段 ${index + 1}</strong>
                <div class="muted">来源：${escapeHtml(item.source || data.filename || '')}</div>
                <div>${displayText(item.content || '')}</div>
              </div>
            `).join('')}
          `;
          saveResult(html);
          stopLoading('analyzeBtn', '文件分析已完成');
        } catch (err) {
          stopLoading('analyzeBtn', '任务失败');
          showError(err);
        }
      }

      async function ingestFolder() {
        try {
          setLoading('正在批量读取文件夹并写入向量库...', 'folderBtn');
          const data = await requestJson('/documents/ingest-folder', {
            folder_path: document.getElementById('folderPath').value,
            reset: document.getElementById('resetBeforeIngest').checked
          });
          showIngestResult(data);
          stopLoading('folderBtn', '文件夹已导入');
        } catch (err) {
          stopLoading('folderBtn', '任务失败');
          showError(err);
        }
      }

      async function analyzeFolder() {
        try {
          setLoading('正在读取文件夹并调用大模型分析...', 'folderAnalyzeBtn');
          const data = await requestJson('/documents/analyze-folder', {
            folder_path: document.getElementById('folderPath').value,
            instruction: document.getElementById('fileInstruction').value,
            max_documents: 12
          });
          const html = `
            <div class="answer">${displayText(data.answer || '')}</div>
            <h3>已读取资料</h3>
            ${(data.preview_documents || []).map((item, index) => `
              <div class="result-item">
                <strong>资料 ${index + 1}</strong>
                <div class="muted">来源：${escapeHtml(item.source || '')}</div>
                <div>${displayText(item.content || '')}</div>
              </div>
            `).join('')}
            ${(data.errors || []).length ? `<h3>未能读取的文件</h3>${data.errors.map((item) => `<div class="result-item"><div>${escapeHtml(item.file)}</div><div class="error">${escapeHtml(item.error)}</div></div>`).join('')}` : ''}
          `;
          saveResult(html);
          stopLoading('folderAnalyzeBtn', '文件夹分析已完成');
        } catch (err) {
          stopLoading('folderAnalyzeBtn', '任务失败');
          showError(err);
        }
      }

      async function loadCounts() {
        try {
          if (document.getElementById('out').innerHTML && !document.getElementById('out').innerHTML.includes('当前数据量')) {
            lastBusinessResultHtml = document.getElementById('out').innerHTML;
          }
          const res = await fetch('/debug/counts');
          const data = await res.json();
          const html = `
            <div class="status-card">
              <h3>当前数据量</h3>
              <p>产品：${data.products}</p>
              <p>文档：${data.documents}</p>
              <p>知识切片：${data.chunks}</p>
              <p>长期记忆：${data.memories}</p>
              <p>爆款案例：${data.viral_cases || 0}</p>
              <p>生成历史：${data.generation_history || 0}</p>
              <div class="hint">点击“返回上次答案”可以回到刚才的生成结果。</div>
            </div>
          `;
          document.getElementById('out').innerHTML = html;
          setStatus('已显示数据量');
        } catch (err) {
          showError(err);
        }
      }

      function fillQuestion(text, mode) {
        switchTab('chat');
        document.getElementById('q').value = text;
        if (mode) document.getElementById('mode').value = mode;
      }
    </script>
  </body>
</html>
"""
