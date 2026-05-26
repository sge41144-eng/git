# Product Operations Agent MVP

本项目是产品运营智能体的第一版骨架，先跑通：

- PostgreSQL + pgvector 向量库
- 产品资料入库
- 文档文本上传入库
- 长期记忆保存
- 基础检索问答

## 启动数据库

```powershell
cd E:\ai-agent\product-agent
docker compose up -d db
```

## 本地启动后端

如果 Docker Hub 拉取 `python:3.12-slim` 超时，可以先用 Windows 本地 Python 跑后端：

```powershell
cd E:\ai-agent\product-agent\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

打开：

```text
http://localhost:8000
http://localhost:8000/docs
```

## 第一版说明

当前没有要求 API Key，所以先使用本地 hashing embedding 作为占位向量器。它适合开发联调，不代表最终检索效果。

后续可替换为：

- OpenAI embedding API
- bge-m3 本地模型
- jina embedding

## 数据目录

数据库数据挂载在：

```text
E:\ai-agent\data\postgres
```

上传文件建议放在：

```text
E:\ai-agent\uploads
```
