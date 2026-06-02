# Stage 4: Embedding 与 RAG 知识库问答

本阶段目标：理解 RAG 的完整链路，并亲手实现一个本地文档问答系统。

## 核心概念

```text
RAG = Retrieval-Augmented Generation = 检索增强生成
RAG 的本质 = 让模型回答前先查资料
```

离线阶段：

```text
文档 -> 加载 -> 切片 -> Embedding -> 存入向量数据库
```

在线阶段：

```text
用户问题 -> 问题 Embedding -> 相似度检索 -> 拼接上下文 -> LLM 生成答案
```

## 目录结构

```text
stage4/
├── README.md
├── docs/
├── indexes/
├── rag_config.py
├── document_loader.py
├── text_splitter.py
├── embedding_model.py
├── vector_store.py
├── rag_pipeline.py
└── rag_cli.py
```

## 依赖安装

```bash
pip install openai sentence-transformers faiss-cpu numpy
```

如果 `faiss-cpu` 安装失败，可以后续改用 Chroma。本项目第一版使用 FAISS，便于理解向量索引和 metadata 的关系。

## 运行前配置

设置火山方舟 API Key：

```bash
export APIKey="你的火山方舟 API Key"
```

## 运行方式

```bash
cd /home/guixuejiang/ws/agents/stage4
python rag_cli.py
```

## CLI 命令

| 命令 | 说明 |
|---|---|
| `/help` | 查看帮助 |
| `/ingest <path>` | 导入单个文件或目录 |
| `/search <question>` | 只检索相关片段，不调用 LLM |
| `/ask <question>` | 基于知识库问答，答案带引用 |
| `/stats` | 查看当前索引状态 |
| `/config` | 查看当前 RAG 参数 |
| `/clear_index` | 清空向量索引和 metadata |
| `quit` / `exit` / `退出` | 退出程序 |

支持导入的文件类型：

```text
.md .txt .py
```

## 推荐练习

导入项目学习计划：

```text
/ingest ../Agent系统学习计划.md
```

导入整个项目目录：

```text
/ingest ../
```

只检索：

```text
/search RAG 和长期记忆有什么区别？
```

问答：

```text
/ask 为什么 RAG 仍然可能答错？
```

## 需要实验的参数

在 `rag_config.py` 中调整：

```python
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 5
MIN_SCORE = 0.25
USE_KEYWORD_RERANK = True
```

建议实验：

| 参数 | 实验值 | 观察点 |
|---|---|---|
| chunk_size | 300 / 800 / 1500 | 太小是否缺上下文，太大是否噪音多 |
| chunk_overlap | 0 / 150 / 300 | 是否减少切断语义的问题 |
| top_k | 3 / 5 / 10 | 答案是否完整，噪音是否变多 |
| rerank | on / off | 排序是否更符合问题 |

## 验收问题

完成后你应该能解释：

- 为什么要切片？
- chunk 太大或太小有什么问题？
- Embedding 是什么？
- 向量数据库解决什么问题？
- RAG 为什么仍然可能答错？
- RAG 和长期记忆有什么区别？
