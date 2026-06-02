# Agent 系统学习计划

## 1. 学习目标

这份学习计划面向已经熟悉 Python 编程、但希望系统理解 AI Agent 体系的新手。

学习完成后，你应该能够理解并实践以下能力：

- 从零搭建一个基础聊天机器人
- 理解短期记忆、长期记忆的作用和实现方式
- 搭建一个基础 RAG 知识库问答系统
- 理解 Tool Calling 的执行机制
- 实现一个简单 Agent 执行循环
- 理解 Skill 如何封装可复用能力
- 理解 MCP 如何标准化连接外部工具和数据源
- 能从系统架构角度讲清楚一个 Agent 系统的来龙去脉

核心目标不是只会调用框架 API，而是理解每一层为什么出现、解决什么问题、如何组合成完整系统。

## 2. 总体发展路线

Agent 系统可以按下面这条能力演进线理解：

```text
Chatbot
↓
短期记忆
↓
长期记忆
↓
RAG 外部知识检索
↓
Tool Calling 工具调用
↓
Agent 多步规划与执行
↓
Skill 可复用能力封装
↓
MCP 标准化工具生态
```

更完整的系统结构是：

```text
用户
↓
Chat UI / CLI
↓
Conversation Manager
↓
短期记忆
↓
长期记忆检索
↓
Agent Orchestrator
↓
任务规划
↓
能力选择
├─ RAG Retriever
├─ Tool Registry
├─ Skill Registry
└─ MCP Client
↓
外部系统
├─ 文档库
├─ 数据库
├─ 文件系统
├─ API
└─ 第三方应用
↓
观察结果
↓
继续执行 / 最终回答
```

## 3. 推荐学习周期

如果每天投入 1-2 小时，建议按 10 周推进。

```text
轻量学习：4-6 周
扎实掌握：8-12 周
工程化掌握：3-6 个月
```

推荐顺序：

```text
第 1 周：LLM 与 Chatbot
第 2 周：Prompt 与短期记忆
第 3 周：长期记忆
第 4 周：Embedding 与向量检索
第 5 周：RAG 问答
第 6 周：工具调用
第 7 周：Agent 执行循环
第 8 周：Skill 系统
第 9 周：MCP
第 10 周：完整 Agent 项目整合
```

## 4. 第 0 阶段：建立全局地图

### 学习目标

先不要急着写复杂 Agent，先建立概念地图。

你需要理解：

```text
LLM 是大脑
Chatbot 是交互入口
Prompt 是指令方式
Context 是短期工作区
Memory 是历史沉淀
RAG 是外部知识检索
Tool 是外部动作能力
Agent 是任务执行中枢
Skill 是可复用任务能力
MCP 是工具连接标准
```

### 核心问题

- 为什么只靠 LLM 不够？
- 为什么需要上下文？
- 为什么需要 RAG？
- 为什么需要工具调用？
- 为什么 Agent 比普通聊天机器人复杂？
- 为什么 Skill 和 MCP 不是同一个东西？

### 输出物

- 画一张自己的 Agent 系统架构图
- 写一篇 1000 字总结：从 Chatbot 到 Agent 的演进

### 验收标准

你能讲清楚：

```text
聊天机器人、RAG、Agent、MCP、Skill 不是并列关系，而是系统中的不同层。
```

## 5. 第 1 阶段：大模型与聊天机器人基础

建议时间：1 周

### 学习目标

理解最基本的大模型调用方式，做出一个最小可用聊天机器人。

### 需要掌握

- LLM API 调用
- Message 格式
- System Prompt
- User Message
- Assistant Message
- Temperature
- Token
- 上下文窗口
- 流式输出
- 错误重试

### 核心概念

```text
LLM 本质是文本预测模型
Chatbot 是 LLM 的一种产品形态
System Prompt 控制角色和行为边界
上下文窗口决定模型一次能看到多少信息
```

### 实践项目：CLI 聊天机器人

最小结构：

```text
用户输入
↓
追加到 messages
↓
调用 LLM
↓
打印回复
↓
把回复追加到 messages
```

示例伪代码：

```python
messages = [
    {"role": "system", "content": "你是一个严谨的 AI 助手。"}
]

while True:
    user_input = input("User: ")
    messages.append({"role": "user", "content": user_input})

    response = call_llm(messages)

    print("AI:", response)
    messages.append({"role": "assistant", "content": response})
```

### 功能要求

- 支持连续多轮对话
- 支持 system prompt
- 支持退出命令
- 支持打印 token 或响应时间

### 验收标准

你能解释：

- 一个最基础 Chatbot 的数据流是什么？
- 短期上下文为什么天然来自 messages？

## 6. 第 2 阶段：Prompt、上下文与短期记忆

建议时间：1 周

### 学习目标

理解短期记忆不是玄学，本质上就是当前上下文的管理。

### 需要掌握

- 上下文拼接
- 对话历史截断
- 摘要式记忆
- 滑动窗口
- 任务状态记录
- Prompt 模板
- 结构化输出
- JSON 输出约束

### 核心概念

```text
短期记忆 = 当前会话中模型可见的信息
```

### 三种短期记忆方式

| 方法 | 说明 | 优点 | 缺点 |
|---|---|---|---|
| 全量历史 | 把所有聊天记录都塞给模型 | 信息完整 | 成本高，容易超上下文 |
| 滑动窗口 | 只保留最近 N 轮对话 | 简单稳定 | 容易丢失早期重要信息 |
| 摘要记忆 | 把旧对话总结成摘要 | 压缩上下文 | 摘要可能丢细节或引入偏差 |

### 实践项目：带短期记忆管理的聊天机器人

功能要求：

- 保存最近 10 轮对话
- 超过长度后自动摘要
- 支持查看当前短期记忆
- 支持清空上下文

可采用的上下文结构：

```text
最近 6 轮对话：原文保留
更早的对话：压缩成 summary
最终 prompt = system prompt + summary + recent messages
```

### 验收标准

你能解释：

- 短期记忆和上下文窗口是什么关系？
- 为什么不是所有历史都应该原样保存？
- 摘要记忆有什么风险？

## 7. 第 3 阶段：长期记忆与用户画像

建议时间：1 周

### 学习目标

理解长期记忆是跨会话的持久化信息，不等于简单保存所有聊天记录。

### 需要掌握

- 长期记忆的分类
- 记忆提取
- 记忆写入
- 记忆更新
- 记忆遗忘
- 记忆检索
- 用户画像
- 任务历史
- 偏好保存

### 长期记忆分类

```text
用户事实：用户是产品经理，熟悉 Python
用户偏好：用户喜欢结构化、例子多的解释
项目背景：用户正在学习 Agent 系统
经验记忆：用户之前偏好使用 FastAPI
任务状态：某个长期项目已经完成到第 3 步
```

### 注意事项

长期记忆不是垃圾桶，不是什么都存。

长期记忆系统需要判断：

- 这条信息是否长期有用？
- 是否涉及隐私？
- 是否可能过期？
- 是否需要用户确认？
- 是否与旧记忆冲突？

### 实践项目：带长期记忆的个人助手

建议使用 SQLite 做一个简单长期记忆系统。

表结构示例：

```text
id
user_id
memory_type
content
confidence
created_at
updated_at
last_used_at
```

最简单流程：

```text
每轮对话结束
↓
让 LLM 判断是否有值得保存的记忆
↓
保存到 SQLite
↓
下次用户提问时检索相关记忆
↓
加入 prompt
```

功能要求：

- 能保存用户偏好
- 能保存用户背景
- 能列出当前记忆
- 能删除指定记忆
- 回答时能使用长期记忆

### 验收标准

你能解释：

- 长期记忆和短期记忆的区别
- 长期记忆和聊天记录的区别
- 长期记忆为什么需要更新和遗忘
- 长期记忆为什么涉及隐私和权限

## 8. 第 4 阶段：Embedding 与 RAG 知识库问答

建议时间：2 周

### 学习目标

理解 RAG 的完整链路，并亲手做一个文档问答系统。

### 需要掌握

- 文档加载
- 文本切片
- Embedding
- 向量数据库
- 相似度检索
- Top-K
- Rerank 重排序
- 上下文拼接
- 引用溯源
- 答案生成
- 幻觉控制

### RAG 基本流程

```text
离线阶段：
文档 → 切片 → 向量化 → 存入向量数据库

在线阶段：
用户问题 → 问题向量化 → 检索相关片段 → 拼接上下文 → LLM 回答
```

RAG 的本质：

```text
让模型回答前先查资料。
```

### 推荐技术栈

- Python
- sentence-transformers 或 OpenAI Embeddings
- FAISS 或 Chroma
- 本地 Markdown / PDF / TXT 文档

### 需要实验的参数

- chunk_size
- chunk_overlap
- top_k
- embedding model
- 是否使用 rerank
- 是否要求引用来源

### 实践项目：本地知识库 RAG 问答系统

功能要求：

- 支持导入文档
- 支持向量化存储
- 支持基于问题检索相关片段
- 支持回答时带引用
- 支持回答“不知道”

### 验收标准

你能解释：

- 为什么要切片？
- chunk 太大或太小有什么问题？
- Embedding 是什么？
- 向量数据库解决什么问题？
- RAG 为什么仍然可能答错？
- RAG 和长期记忆有什么区别？

## 9. 第 5 阶段：Tool Calling 工具调用

建议时间：1 周

### 学习目标

让 AI 从“只能说”变成“可以做”。

### 需要掌握

- 函数调用
- 工具描述
- 参数 schema
- 工具选择
- 工具执行
- 工具结果回传
- 错误处理
- 权限控制

### 工具调用流程

```text
用户提出需求
↓
LLM 判断需要调用工具
↓
LLM 输出工具名和参数
↓
程序执行工具
↓
把工具结果返回给 LLM
↓
LLM 生成最终回答
```

### 建议实现的工具

- calculator：计算表达式
- get_current_time：获取当前时间
- search_docs：检索本地知识库
- read_file：读取指定安全目录下文件
- write_note：写入笔记

### 注意事项

- 工具必须有边界
- 不能让模型随便执行系统命令
- 工具参数需要校验
- 工具调用失败要能反馈
- 敏感操作要用户确认

### 实践项目：支持工具调用的 AI 助手

功能要求：

- 支持至少 5 个工具
- LLM 能自动选择工具
- 工具结果能回传给 LLM
- 支持工具调用日志
- 支持工具错误处理

### 验收标准

你能解释：

- Tool Calling 和普通 Prompt 有什么区别？
- 为什么工具描述很重要？
- 为什么工具需要权限控制？
- 为什么工具返回结果还要再给 LLM 总结？

## 10. 第 6 阶段：Agent 规划与执行循环

建议时间：2 周

### 学习目标

理解 Agent 的本质：围绕目标进行多步规划、工具调用、观察反馈和迭代执行。

### 需要掌握

- 任务拆解
- 计划生成
- ReAct 模式
- Plan-and-Execute
- 执行循环
- 状态管理
- Observation
- Reflection
- 终止条件
- 最大步数限制
- 异常恢复

### 简单 Agent 循环

```text
用户目标
↓
LLM 思考下一步
↓
选择工具
↓
执行工具
↓
观察结果
↓
判断是否完成
↓
未完成则继续
↓
输出最终答案
```

经典结构：

```text
Thought：我需要做什么
Action：我要调用哪个工具
Action Input：工具参数
Observation：工具返回了什么
Final Answer：最终回答
```

### 实践项目：迷你 Agent 执行器

功能要求：

- 输入一个目标
- Agent 自动拆解任务
- Agent 自动选择工具
- Agent 可多步执行
- Agent 能判断任务完成
- Agent 输出过程日志和最终答案

### 保护机制

- 最大执行步数
- 工具白名单
- 失败重试次数
- 用户确认机制
- 日志记录
- 中间状态可查看

### 验收标准

你能解释：

- Agent 和 Chatbot 的本质区别
- Agent 和 RAG 的区别
- 为什么 Agent 需要工具
- 为什么 Agent 需要状态管理
- 为什么 Agent 需要终止条件
- 为什么 Agent 容易失控

## 11. 第 7 阶段：Skill 能力封装

建议时间：1 周

### 学习目标

理解 Skill 是对高频任务能力的沉淀，不是单个工具。

### 需要掌握

- Skill 定义
- Skill 触发条件
- Skill 输入输出
- Skill 执行步骤
- Skill 使用的工具
- Skill 约束
- Skill 示例
- Skill 版本管理

### 核心理解

```text
Tool 是动作
Skill 是方法
```

例如：

```text
Tool：搜索网页
Skill：竞品分析
```

### Skill 示例

```yaml
name: competitor_analysis
description: 用于竞品分析
inputs:
  - product_name
  - competitors
steps:
  - 确认分析维度
  - 搜索竞品资料
  - 提取功能、定价、目标用户
  - 形成对比表
  - 总结机会点
outputs:
  - 竞品对比表
  - 机会点总结
tools:
  - web_search
  - read_url
  - summarize
constraints:
  - 必须注明来源
  - 不确定信息要标注
```

### 实践项目：支持 Skill 的 Agent

建议实现 3 个 Skill：

- 学习笔记 Skill
- 竞品分析 Skill
- PRD 草稿 Skill

功能要求：

- Agent 能根据任务选择 Skill
- Skill 能指导 Agent 执行步骤
- Skill 能规定输出格式
- Skill 可以复用已有工具

### 验收标准

你能解释：

- 为什么 Skill 不是 Tool？
- 为什么 Skill 可以降低 Agent 随机性？
- 为什么 Skill 适合沉淀领域经验？
- Skill 和 Workflow 有什么相似和不同？

## 12. 第 8 阶段：MCP 与工具生态

建议时间：1-2 周

### 学习目标

理解 MCP 是 Agent 连接外部工具和数据源的标准协议。

### 需要掌握

- MCP Host
- MCP Client
- MCP Server
- Tools
- Resources
- Prompts
- stdio transport
- HTTP/SSE transport
- 权限边界
- 工具发现

### 核心角色

```text
MCP Host：AI 应用，比如 Claude Desktop、Cursor、OpenCode
MCP Client：Host 内部连接 MCP Server 的模块
MCP Server：提供工具和资源的服务
```

### MCP 的价值

- 统一工具接入标准
- 让工具可被多个 Agent 应用复用
- 降低插件开发成本
- 把数据源、工具、Prompt 暴露给 AI

### 实践项目：个人笔记 MCP Server

建议用 Python 写一个最小 MCP Server。

提供工具：

- add_numbers
- search_notes
- read_note
- create_note

功能要求：

- MCP Server 能暴露笔记查询工具
- MCP Server 能暴露笔记读取工具
- MCP Server 能被 MCP Host 发现和调用

### 验收标准

你能解释：

- MCP 和 API 的关系
- MCP 和 Tool Calling 的关系
- MCP 和 Skill 的区别
- 为什么 MCP 对 Agent 生态重要
- 为什么 MCP 不是 Agent 本身

## 13. 第 9 阶段：完整 Agent 系统整合项目

建议时间：2-4 周

### 最终项目：AI 学习研究助理 Agent

用户输入一个学习主题，例如：

```text
请帮我研究 Agent、RAG、MCP 的关系，并生成一份学习笔记。
```

系统自动完成：

```text
理解目标
读取长期记忆，知道用户偏好
选择学习研究 Skill
检索本地知识库 RAG
必要时调用搜索工具
整理资料
生成结构化学习笔记
保存结果
更新长期记忆
```

### 建议模块划分

```text
llm_client.py
memory_short.py
memory_long.py
rag_index.py
tools.py
agent.py
skills.py
mcp_server.py
main.py
```

### 功能清单

- 多轮对话
- 短期记忆
- 长期记忆
- 文档 RAG
- 工具调用
- Agent 多步执行
- Skill 选择
- MCP 工具接入
- 执行日志
- 错误处理

### 最终验收标准

你应该能做到：

- 从代码层面讲清楚一次用户请求如何流转
- 能解释每个模块为什么存在
- 能替换不同 LLM
- 能替换不同向量数据库
- 能新增一个 Tool
- 能新增一个 Skill
- 能新增一个 MCP Server
- 能判断一个问题适合 Chat、RAG 还是 Agent

## 14. 10 周执行表

| 周数 | 主题 | 实践项目 | 输出物 |
|---|---|---|---|
| 第 1 周 | LLM 与 Chatbot | CLI 聊天机器人 | chatbot.py，Chatbot 基本结构总结 |
| 第 2 周 | Prompt 与短期记忆 | 上下文管理机器人 | short_memory.py，支持摘要的聊天机器人 |
| 第 3 周 | 长期记忆 | 个人记忆助手 | long_memory.py，memory.db |
| 第 4 周 | Embedding 与向量检索 | 文档向量索引 | rag_index.py，文档导入脚本 |
| 第 5 周 | RAG 问答 | 本地知识库问答 | rag_qa.py，带引用的答案生成 |
| 第 6 周 | 工具调用 | Tool Calling 助手 | tools.py，tool_registry.py |
| 第 7 周 | Agent 执行循环 | Mini Agent | agent.py，多步工具调用 Agent |
| 第 8 周 | Skill 系统 | Skill Agent | study_note.yaml，competitor_analysis.yaml，prd_draft.yaml |
| 第 9 周 | MCP | 个人笔记 MCP Server | mcp_note_server.py |
| 第 10 周 | 系统整合 | AI 学习研究助理 | 完整项目，README，架构图，执行日志 |

## 15. 建议技术栈

### 底层理解优先

- Python
- OpenAI-compatible API
- SQLite
- FAISS 或 Chroma
- sentence-transformers 或 OpenAI Embedding
- Pydantic
- FastAPI，可选
- MCP Python SDK

### 后期可学习框架

- LangChain
- LlamaIndex
- LangGraph
- AutoGen
- CrewAI
- Haystack

建议前 6 周尽量少用大框架，先自己写简化版。

原因：

```text
如果一开始就用框架，你会知道怎么调 API，但不一定知道 Agent 内部为什么这样工作。
```

## 16. 容易踩的坑

### 坑 1：把 Agent 当成更高级的 Chatbot

正确理解：

```text
Chatbot 主要回答问题
Agent 主要完成任务
```

### 坑 2：把 RAG 当成 Agent

正确理解：

```text
RAG 是检索知识
Agent 是组织行动
```

### 坑 3：把长期记忆当成聊天记录

正确理解：

```text
聊天记录是原始数据
长期记忆是经过筛选和结构化的高价值信息
```

### 坑 4：把 Tool 和 Skill 混在一起

正确理解：

```text
Tool 是动作
Skill 是方法
```

### 坑 5：把 MCP 当成 Agent 框架

正确理解：

```text
MCP 是连接协议，不是 Agent 本身
```

### 坑 6：过早使用复杂框架

正确做法：

```text
先手写最小版本
再使用框架提升工程效率
```

## 17. 推荐学习资源方向

官方文档优先：

- OpenAI / Anthropic / Gemini / Qwen API 文档
- MCP 官方文档
- LangGraph 官方文档
- LlamaIndex 官方文档
- Chroma / FAISS 文档
- Pydantic 文档

关键词搜索建议：

- LLM chat completion
- prompt engineering
- context window
- conversation memory
- RAG from scratch
- embedding vector database
- function calling
- tool calling
- ReAct agent
- plan and execute agent
- LangGraph agent
- MCP server python
- agent memory architecture

建议论文或经典材料：

- ReAct: Synergizing Reasoning and Acting in Language Models
- Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
- Toolformer
- MRKL Systems
- Reflexion

不需要一开始就精读论文，可以先看解读，再回头读原文。

## 18. 最终能力目标

按这份计划学完后，你应该具备以下能力：

- 能从零写一个多轮聊天机器人
- 能实现短期记忆管理
- 能设计长期记忆结构
- 能实现一个简单 RAG 系统
- 能实现工具调用机制
- 能写一个基础 Agent 执行循环
- 能设计和加载 Skill
- 能写简单 MCP Server
- 能把这些模块组合成完整 Agent 系统
- 能判断不同业务场景该用 Chatbot、RAG 还是 Agent

更重要的是，你会理解：

```text
Agent 系统不是一个单点技术，而是一套围绕“理解目标、获取上下文、调用能力、执行任务、反馈调整”的系统工程。
```

## 19. 建议从第一个项目开始

第一个目标：

```text
用 Python 写一个 CLI 多轮聊天机器人。
```

然后每周加一层能力：

```text
第 1 版：能聊天
第 2 版：有短期记忆
第 3 版：有长期记忆
第 4 版：能查文档
第 5 版：能调用工具
第 6 版：能多步执行
第 7 版：能选择 Skill
第 8 版：能接 MCP
```

这条路径非常适合 Python 熟悉者，因为每一层都能通过代码验证，不会停留在概念层。
