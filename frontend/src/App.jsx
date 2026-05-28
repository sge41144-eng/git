import { useMemo, useState } from 'react'
import './App.css'
import { API_BASE, deleteJson, getJson, postForm, postJson } from './api'

const T = {
  app: '产品运营智能体',
  subtitle: 'React 前端工作台',
  chat: '对话助手',
  content: '热点创作',
  files: '资料中心',
  benchmark: '对标创作',
  history: '生成历史',
  product: '产品入库',
  memory: '长期记忆',
  statusReady: '前端已启动，等待操作',
  sourceMode: '资料来源模式',
  answerMode: '回答模式',
  topK: '参考资料数',
  input: '输入消息',
  send: '发送',
  thinking: '思考中...',
  clear: '清空本轮对话',
  output: '结果输出',
  counts: '查看数据量',
  submit: '提交',
  save: '保存',
}

const tabs = [
  ['chat', T.chat],
  ['content', T.content],
  ['files', T.files],
  ['benchmark', T.benchmark],
  ['history', T.history],
  ['product', T.product],
  ['memory', T.memory],
]

const sourceModeLabels = {
  knowledge_only: '只查我的知识库',
  llm_only: '通用大模型回答',
  knowledge_llm: '知识库 + 大模型',
  web_knowledge_llm: '知识库 + 联网搜索 + 大模型',
}

const answerModes = [
  ['assistant', '运营助手'],
  ['qa', '产品问答'],
  ['customer_service', '客服话术'],
  ['script', '内容脚本'],
  ['campaign', '活动策划'],
]

const contentModules = [
  ['short_video', '短视频脚本'],
  ['seo_article', 'SEO 搜索图文'],
  ['product_photo_post', '产品实拍图文'],
  ['caption_copy', '字幕/口播文案'],
  ['recommendation_post', '推荐种草方向'],
  ['viral_format_mimic', '爆款格式模仿'],
]

function App() {
  const [activeTab, setActiveTab] = useState('chat')
  const [status, setStatus] = useState(T.statusReady)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [messages, setMessages] = useState([])
  const [chat, setChat] = useState({
    message: '',
    mode: 'assistant',
    source_mode: 'knowledge_llm',
    top_k: 6,
    auto_memory: true,
  })
  const [content, setContent] = useState({
    product: '',
    platform: '抖音',
    goal: '种草转化',
    audience: '',
    content_module: 'short_video',
    keywords: '',
    seo_goal: '',
    image_requirements: '',
    reference_style: '',
    extra_requirements: '',
  })
  const [product, setProduct] = useState({
    name: '',
    category: '',
    target_audience: '',
    selling_points: '',
    cautions: '',
    knowledge_text: '',
  })
  const [memoryText, setMemoryText] = useState('')
  const [folderPath, setFolderPath] = useState('E:\\ai-agent\\uploads\\产品资料')
  const [resetFolder, setResetFolder] = useState(false)
  const [fileInstruction, setFileInstruction] = useState('请分析这个文件的核心内容、可用于产品运营的要点和风险。')
  const [file, setFile] = useState(null)
  const [benchmarkFile, setBenchmarkFile] = useState(null)
  const [benchmark, setBenchmark] = useState({
    reference_text: '',
    product: '',
    platform: '小红书',
    audience: '',
    keywords: '',
    requirement: '',
  })

  const title = useMemo(() => tabs.find(([key]) => key === activeTab)?.[1] || T.app, [activeTab])

  function update(setter, key, value) {
    setter((prev) => ({ ...prev, [key]: value }))
  }

  async function run(task, ok) {
    setLoading(true)
    setStatus('正在处理...')
    try {
      const data = await task()
      setResult(data)
      setStatus(ok || '任务已完成')
      return data
    } catch (error) {
      setResult({ error: error.message })
      setStatus('任务失败')
      return null
    } finally {
      setLoading(false)
    }
  }

  async function sendChat() {
    const message = chat.message.trim()
    if (!message || loading) return
    const history = messages.slice(-24).map(({ role, content }) => ({ role, content }))
    setMessages((prev) => [...prev, { role: 'user', content: message }])
    update(setChat, 'message', '')
    setLoading(true)
    setStatus('正在生成回答...')
    try {
      const data = await postJson('/chat', {
        message,
        session_id: 'browser-react',
        mode: chat.mode,
        source_mode: chat.source_mode,
        top_k: Number(chat.top_k),
        history,
        auto_memory: chat.auto_memory,
      })
      const meta = [
        `${T.sourceMode}：${sourceModeLabels[data.source_mode] || data.source_mode}`,
        `参考资料：${data.retrieved?.length || 0} 条`,
        data.session_summary ? '已读取会话摘要' : '',
        data.session_summary_updated ? '会话摘要已更新' : '',
        data.web_results?.length ? `联网线索：${data.web_results.length} 条` : '',
        data.auto_memory_saved ? '已写入长期记忆' : '',
      ].filter(Boolean).join(' · ')
      setMessages((prev) => [...prev, { role: 'assistant', content: data.answer || '', meta }])
      setResult(data)
      setStatus('回答已生成')
    } catch (error) {
      setMessages((prev) => [...prev, { role: 'assistant', content: `操作失败：${error.message}` }])
      setStatus('回答失败')
    } finally {
      setLoading(false)
    }
  }

  const actions = {
    content: () => run(() => postJson('/workflows/content', { ...content, top_k: 6, search_limit: 4 }), '内容方案已生成'),
    product: () => run(() => postJson('/products', product), '产品已保存并入库'),
    memory: () => run(() => postJson('/memories', { memory_type: 'user_preference', content: memoryText, importance: 4 }), '长期记忆已保存'),
    counts: () => run(() => getJson('/debug/counts'), '数据量已读取'),
    history: () => run(() => getJson('/generation-history'), '生成历史已读取'),
    ingestFolder: () => run(() => postJson('/documents/ingest-folder', { folder_path: folderPath, reset: resetFolder }), '文件夹已入库'),
    analyzeFolder: () => run(() => postJson('/documents/analyze-folder', { folder_path: folderPath, instruction: fileInstruction, max_documents: 10 }), '文件夹分析完成'),
    upload: (path) => {
      if (!file) {
        setStatus('请先选择文件')
        return null
      }
      const form = new FormData()
      form.append('file', file)
      if (path.includes('analyze')) form.append('instruction', fileInstruction)
      return run(() => postForm(path, form), path.includes('analyze') ? '文件分析完成' : '文件已入库')
    },
    benchmark: () => {
      const form = new FormData()
      if (benchmarkFile) form.append('file', benchmarkFile)
      Object.entries(benchmark).forEach(([key, value]) => form.append(key, value))
      return run(() => postForm('/workflows/benchmark', form), '对标创作已生成')
    },
    deleteHistory: (id) => run(async () => {
      await deleteJson(`/generation-history/${id}`)
      return getJson('/generation-history')
    }, '历史记录已删除'),
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">AI</div>
          <div>
            <div className="brand-title">{T.app}</div>
            <div className="brand-subtitle">{T.subtitle}</div>
          </div>
        </div>
        <nav className="tabs">
          {tabs.map(([key, label]) => (
            <button key={key} className={activeTab === key ? 'active' : ''} onClick={() => setActiveTab(key)}>
              {label}
            </button>
          ))}
        </nav>
        <div className="sidebar-foot">
          <span>{API_BASE}</span>
          <a href={`${API_BASE}/docs`} target="_blank" rel="noreferrer">接口文档</a>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <h1>{title}</h1>
            <p>知识库、联网搜索、长期记忆和运营创作已拆到独立 React 前端。</p>
          </div>
          <div className="status-pill">{loading ? '处理中' : status}</div>
        </header>

        <div className="work-grid">
          <section className="panel control-panel">
            {activeTab === 'chat' && <ChatPanel chat={chat} setChat={setChat} update={update} send={sendChat} clear={() => setMessages([])} loading={loading} />}
            {activeTab === 'content' && <ContentPanel form={content} setForm={setContent} update={update} submit={actions.content} loading={loading} />}
            {activeTab === 'files' && <FilesPanel fileInstruction={fileInstruction} setFileInstruction={setFileInstruction} setFile={setFile} folderPath={folderPath} setFolderPath={setFolderPath} resetFolder={resetFolder} setResetFolder={setResetFolder} actions={actions} loading={loading} />}
            {activeTab === 'benchmark' && <BenchmarkPanel form={benchmark} setForm={setBenchmark} update={update} setFile={setBenchmarkFile} submit={actions.benchmark} loading={loading} />}
            {activeTab === 'history' && <SimplePanel title={T.history} text="查看内容创作、对标创作等历史结果。" button="读取生成历史" onClick={actions.history} loading={loading} />}
            {activeTab === 'product' && <ProductPanel form={product} setForm={setProduct} update={update} submit={actions.product} loading={loading} />}
            {activeTab === 'memory' && <MemoryPanel value={memoryText} setValue={setMemoryText} save={actions.memory} counts={actions.counts} loading={loading} />}
          </section>

          <section className="panel output-panel">
            <div className="output-head">
              <div>
                <h2>{T.output}</h2>
                <p>{status}</p>
              </div>
              <button className="ghost" onClick={actions.counts}>{T.counts}</button>
            </div>
            {activeTab === 'chat' ? <ChatOutput messages={messages} /> : <ResultView data={result} onDeleteHistory={actions.deleteHistory} />}
          </section>
        </div>
      </main>
    </div>
  )
}

function ChatPanel({ chat, setChat, update, send, clear, loading }) {
  return (
    <>
      <h2>{T.chat}</h2>
      <p className="section-kicker">选择资料来源模式后，像和运营同事聊天一样提问。</p>
      <div className="grid2">
        <label>{T.answerMode}<Select value={chat.mode} onChange={(v) => update(setChat, 'mode', v)} options={answerModes} /></label>
        <label>{T.sourceMode}<Select value={chat.source_mode} onChange={(v) => update(setChat, 'source_mode', v)} options={Object.entries(sourceModeLabels)} /></label>
      </div>
      <label>{T.topK}<Select value={String(chat.top_k)} onChange={(v) => update(setChat, 'top_k', Number(v))} options={[['4', '4'], ['6', '6'], ['8', '8'], ['10', '10']]} /></label>
      <label className="inline-check">
        <input type="checkbox" checked={chat.auto_memory} onChange={(e) => update(setChat, 'auto_memory', e.target.checked)} />
        自动维护会话摘要，并沉淀有价值长期记忆
      </label>
      <div className="quick">
        <button type="button" onClick={() => update(setChat, 'message', '生命阳光牛初乳和天美健牛初乳对比，我们有什么优势？只分析产品优劣势，不要客服话术。')}>竞品优势</button>
        <button type="button" onClick={() => update(setChat, 'message', '请根据知识库介绍一下目前有哪些产品资料')}>资料概览</button>
      </div>
      <label>{T.input}<textarea rows="7" value={chat.message} onChange={(e) => update(setChat, 'message', e.target.value)} /></label>
      <div className="button-row">
        <button className="secondary" type="button" onClick={clear}>{T.clear}</button>
        <button type="button" disabled={loading} onClick={send}>{loading ? T.thinking : T.send}</button>
      </div>
    </>
  )
}

function ContentPanel({ form, setForm, update, submit, loading }) {
  return (
    <>
      <h2>{T.content}</h2>
      <p className="section-kicker">联网搜索公开线索，结合知识库、长期记忆和案例库生成内容方案。</p>
      <label>产品/主题<input value={form.product} onChange={(e) => update(setForm, 'product', e.target.value)} /></label>
      <div className="grid2">
        <label>平台<input value={form.platform} onChange={(e) => update(setForm, 'platform', e.target.value)} /></label>
        <label>创作模块<Select value={form.content_module} onChange={(v) => update(setForm, 'content_module', v)} options={contentModules} /></label>
      </div>
      <label>目标<input value={form.goal} onChange={(e) => update(setForm, 'goal', e.target.value)} /></label>
      <label>关键词/SEO词<input value={form.keywords} onChange={(e) => update(setForm, 'keywords', e.target.value)} /></label>
      <label>目标人群<input value={form.audience} onChange={(e) => update(setForm, 'audience', e.target.value)} /></label>
      <label>SEO搜索方向<textarea rows="3" value={form.seo_goal} onChange={(e) => update(setForm, 'seo_goal', e.target.value)} /></label>
      <label>产品实拍/配图要求<textarea rows="3" value={form.image_requirements} onChange={(e) => update(setForm, 'image_requirements', e.target.value)} /></label>
      <label>参考/模仿格式<textarea rows="3" value={form.reference_style} onChange={(e) => update(setForm, 'reference_style', e.target.value)} /></label>
      <label>额外要求<textarea rows="4" value={form.extra_requirements} onChange={(e) => update(setForm, 'extra_requirements', e.target.value)} /></label>
      <button type="button" disabled={loading} onClick={submit}>{loading ? '生成中...' : '联网生成内容方案'}</button>
    </>
  )
}

function FilesPanel({ fileInstruction, setFileInstruction, setFile, folderPath, setFolderPath, resetFolder, setResetFolder, actions, loading }) {
  return (
    <>
      <h2>{T.files}</h2>
      <p className="section-kicker">上传文件、分析资料，或把本地文件夹批量向量化入库。</p>
      <label>上传文件<input type="file" accept=".txt,.md,.csv,.xlsx,.xls,.pdf" onChange={(e) => setFile(e.target.files?.[0] || null)} /></label>
      <label>分析指令<textarea rows="3" value={fileInstruction} onChange={(e) => setFileInstruction(e.target.value)} /></label>
      <div className="button-row">
        <button disabled={loading} onClick={() => actions.upload('/documents/upload')}>上传并入库</button>
        <button className="secondary" disabled={loading} onClick={() => actions.upload('/documents/analyze-upload')}>只分析文件</button>
      </div>
      <label>本地文件夹路径<input value={folderPath} onChange={(e) => setFolderPath(e.target.value)} /></label>
      <label className="inline-check"><input type="checkbox" checked={resetFolder} onChange={(e) => setResetFolder(e.target.checked)} />导入前清空现有知识库</label>
      <div className="button-row">
        <button disabled={loading} onClick={actions.ingestFolder}>导入文件夹并向量化</button>
        <button className="secondary" disabled={loading} onClick={actions.analyzeFolder}>只分析文件夹</button>
      </div>
    </>
  )
}

function BenchmarkPanel({ form, setForm, update, setFile, submit, loading }) {
  return (
    <>
      <h2>{T.benchmark}</h2>
      <p className="section-kicker">粘贴或上传对标作品，拆解结构后生成适合你产品的原创版本。</p>
      <label>上传对标文件<input type="file" accept=".txt,.md,.csv,.xlsx,.xls,.pdf,.png,.jpg,.jpeg" onChange={(e) => setFile(e.target.files?.[0] || null)} /></label>
      <label>对标内容<textarea rows="6" value={form.reference_text} onChange={(e) => update(setForm, 'reference_text', e.target.value)} /></label>
      <label>我的产品<input value={form.product} onChange={(e) => update(setForm, 'product', e.target.value)} /></label>
      <div className="grid2">
        <label>平台<input value={form.platform} onChange={(e) => update(setForm, 'platform', e.target.value)} /></label>
        <label>目标人群<input value={form.audience} onChange={(e) => update(setForm, 'audience', e.target.value)} /></label>
      </div>
      <label>关键词<input value={form.keywords} onChange={(e) => update(setForm, 'keywords', e.target.value)} /></label>
      <label>创作要求<textarea rows="4" value={form.requirement} onChange={(e) => update(setForm, 'requirement', e.target.value)} /></label>
      <button disabled={loading} onClick={submit}>生成对标创作方案</button>
    </>
  )
}

function ProductPanel({ form, setForm, update, submit, loading }) {
  return (
    <>
      <h2>{T.product}</h2>
      <p className="section-kicker">保存后会自动切片并写入向量库。</p>
      {[
        ['name', '产品名称'],
        ['category', '产品类目'],
        ['target_audience', '目标人群'],
      ].map(([key, label]) => <label key={key}>{label}<input value={form[key]} onChange={(e) => update(setForm, key, e.target.value)} /></label>)}
      {[
        ['selling_points', '核心卖点'],
        ['cautions', '宣传注意事项'],
        ['knowledge_text', '补充知识'],
      ].map(([key, label]) => <label key={key}>{label}<textarea rows={key === 'knowledge_text' ? 5 : 3} value={form[key]} onChange={(e) => update(setForm, key, e.target.value)} /></label>)}
      <button disabled={loading} onClick={submit}>保存产品并入库</button>
    </>
  )
}

function MemoryPanel({ value, setValue, save, counts, loading }) {
  return (
    <>
      <h2>{T.memory}</h2>
      <p className="section-kicker">写入品牌规则、回答偏好、固定卖点和禁用表达。</p>
      <label>记忆内容<textarea rows="7" value={value} onChange={(e) => setValue(e.target.value)} /></label>
      <div className="button-row">
        <button disabled={loading} onClick={save}>保存长期记忆</button>
        <button className="secondary" disabled={loading} onClick={counts}>查看数据量</button>
      </div>
    </>
  )
}

function SimplePanel({ title, text, button, onClick, loading }) {
  return (
    <>
      <h2>{title}</h2>
      <p className="section-kicker">{text}</p>
      <button disabled={loading} onClick={onClick}>{button}</button>
    </>
  )
}

function Select({ value, onChange, options }) {
  return <select value={value} onChange={(e) => onChange(e.target.value)}>{options.map(([v, label]) => <option key={v} value={v}>{label}</option>)}</select>
}

function ChatOutput({ messages }) {
  if (!messages.length) return <div className="empty">选择资料来源模式后开始对话。右侧会固定在这个窗口内滚动。</div>
  return (
    <div className="chat-feed">
      {messages.map((item, index) => (
        <div className={`chat-row ${item.role}`} key={`${item.role}-${index}`}>
          <div className="chat-role">{item.role === 'user' ? '你' : '运营助手'}</div>
          <div className="chat-bubble">{item.content}</div>
          {item.meta && <div className="chat-meta">{item.meta}</div>}
        </div>
      ))}
    </div>
  )
}

function ResultView({ data, onDeleteHistory }) {
  if (!data) return <div className="empty">执行任务后，结果会显示在这里。</div>
  if (data.error) return <div className="error">{data.error}</div>
  if (Array.isArray(data)) {
    return (
      <div className="result-list">
        {data.map((item) => (
          <article className="result-card" key={item.id || item.title}>
            <div className="result-card-head">
              <strong>{item.goal || item.title || item.product || item.workflow || item.id}</strong>
              {item.id && <button className="ghost danger" onClick={() => onDeleteHistory(item.id)}>删除</button>}
            </div>
            <p>{item.output_content || item.analysis || item.content || JSON.stringify(item)}</p>
          </article>
        ))}
      </div>
    )
  }
  if (data.answer) {
    return (
      <div className="report">
        <div className="answer">{data.answer}</div>
        <MetaBlocks data={data} />
      </div>
    )
  }
  return <pre className="json-output">{JSON.stringify(data, null, 2)}</pre>
}

function MetaBlocks({ data }) {
  const blocks = [
    ['联网线索', data.trends || data.web_results],
    ['搜索诊断', data.search_diagnostics],
    ['参考资料', data.retrieved],
    ['爆款案例', data.viral_cases],
    ['解析来源', data.parsed_sources],
  ].filter(([, value]) => Array.isArray(value) && value.length)

  return (
    <div className="meta-blocks">
      {blocks.map(([title, items]) => (
        <section className="meta-block" key={title}>
          <h3>{title}<span>{items.length} 条</span></h3>
          {items.slice(0, 8).map((item, index) => (
            <div className="mini-card" key={`${title}-${index}`}>
              <strong>{item.title || item.query || item.source || item.metadata?.product_name || `资料 ${index + 1}`}</strong>
              <p>{item.snippet || item.content || item.reason || JSON.stringify(item)}</p>
            </div>
          ))}
        </section>
      ))}
    </div>
  )
}

export default App
