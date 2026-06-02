# Agent 系统学习项目

这是一个按阶段推进的 AI Agent 学习项目，目标是从基础模型调用开始，逐步掌握短期记忆、长期记忆、RAG、工具调用、Agent 执行循环和 Skill 能力封装。

## 项目结构

```text
.
├── Agent系统学习计划.md
├── stage1/
├── stage2/
├── stage3/
├── stage4/
├── stage5/
├── stage6/
└── stage7/
```

## 阶段说明

| 阶段 | 目录 | 主题 | 核心目标 |
|---|---|---|---|
| 第 1 阶段 | `stage1/` | 模型 API 调用 | 掌握 OpenAI SDK / 火山方舟 API 的基础调用 |
| 第 2 阶段 | `stage2/` | Prompt、上下文与短期记忆 | 理解短期记忆本质是上下文管理 |
| 第 3 阶段 | `stage3/` | 长期记忆与用户画像 | 使用 SQLite 实现跨会话长期记忆 |
| 第 4 阶段 | `stage4/` | Embedding 与 RAG | 构建本地知识库问答系统 |
| 第 5 阶段 | `stage5/` | Tool Calling 工具调用 | 让 AI 能自动选择并调用工具 |
| 第 6 阶段 | `stage6/` | Agent 规划与执行循环 | 实现多步规划、执行、观察和总结 |
| 第 7 阶段 | `stage7/` | Skill 能力封装 | 将高频任务沉淀为可复用 Skill |

## 环境准备

建议使用 Python 虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate
```

安装基础依赖：

```bash
pip install openai
```

部分阶段需要额外依赖：

```bash
pip install sentence-transformers faiss-cpu numpy pyyaml
```

## API Key 配置

本项目使用火山方舟 OpenAI 兼容接口。

运行前需要设置环境变量：

```bash
export APIKey="你的火山方舟 API Key"
```

代码中统一使用：

```python
OpenAI(
    api_key=os.getenv("APIKey"),
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)
```

## 各阶段运行方式

### Stage 1

```bash
cd stage1
python model_request.py
```

### Stage 2

```bash
cd stage2
python short_memerry.py
```

### Stage 3

```bash
cd stage3
python long_memory_chatbot.py
```

### Stage 4

```bash
cd stage4
python rag_cli.py
```

### Stage 5

```bash
cd stage5
python tool_calling_assistant.py
```

### Stage 6

```bash
cd stage6
python mini_agent.py
```

### Stage 7

```bash
cd stage7
python skill_agent.py
```

## 学习主线

本项目按以下路径逐步构建 Agent 系统能力：

```text
模型调用
↓
短期记忆
↓
长期记忆
↓
RAG 知识库
↓
工具调用
↓
Agent 执行循环
↓
Skill 能力封装
```

## 核心理解

### 短期记忆

```text
短期记忆 = 当前会话中模型可见的信息
```

### 长期记忆

```text
长期记忆 = 跨会话保存、经过筛选、可检索和可删除的有用信息
```

### RAG

```text
RAG = 让模型回答前先查资料
```

### Tool Calling

```text
Tool 是动作
模型决定是否调用工具
程序负责真正执行工具
```

### Agent

```text
Agent = 围绕目标进行多步规划、工具调用、观察反馈和迭代执行的系统
```

### Skill

```text
Tool 是动作
Skill 是方法
```

## 注意事项

- 不要把 API Key 写入代码。
- 不要提交 `.env`、数据库、日志、向量索引等运行产物。
- 已通过 `.gitignore` 忽略常见运行产物。
- `stage4` 的 RAG 索引需要先执行 `/ingest` 才能检索。
- `stage5` 之后的工具和 Agent 会涉及文件读取/写入，注意权限边界。
- `write_note` 等写入工具执行前应进行用户确认。

## 推荐学习方式

1. 先阅读 `Agent系统学习计划.md`。
2. 按 `stage1` 到 `stage7` 顺序运行项目。
3. 每个阶段先理解 README，再运行代码。
4. 修改参数并观察行为变化。
5. 用自己的话回答每个阶段的验收问题。
