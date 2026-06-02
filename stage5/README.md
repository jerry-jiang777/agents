# Stage 5: Tool Calling 工具调用

本阶段目标：让 AI 从“只能说”变成“可以做”。

## 核心流程

```text
用户提出需求
↓
LLM 判断是否需要调用工具
↓
LLM 输出工具名和参数
↓
程序校验参数和权限
↓
程序执行工具
↓
把工具结果返回给 LLM
↓
LLM 生成最终回答
```

关键点：LLM 不直接执行工具，真正执行工具的是你的程序。

## 项目结构

```text
stage5/
├── README.md
├── tool_calling_assistant.py
├── tool_schemas.py
├── tools.py
├── tool_executor.py
├── permissions.py
├── tool_logger.py
├── notes/
└── tool_logs.jsonl
```

## 支持的工具

| 工具 | 说明 |
|---|---|
| `calculator` | 安全计算数学表达式 |
| `get_current_time` | 获取当前时间 |
| `search_docs` | 检索第 4 阶段 RAG 本地知识库 |
| `read_file` | 读取项目安全目录下的文件 |
| `write_note` | 写入学习笔记到 `stage5/notes/` |

## 安全边界

- 不提供任意 shell 执行工具。
- `calculator` 不直接使用不受控的 `eval`。
- `read_file` 只能读取项目目录下允许类型的文件。
- `read_file` 禁止读取 `.env`、数据库、密钥等敏感文件。
- `write_note` 只能写入 `stage5/notes/`。
- `write_note` 执行前需要用户确认。
- 所有工具调用都会写入 `tool_logs.jsonl`。

## 运行方式

设置火山方舟 API Key：

```bash
export APIKey="你的火山方舟 API Key"
```

运行：

```bash
cd /home/guixuejiang/ws/agents/stage5
python tool_calling_assistant.py
```

## 测试问题

```text
现在几点？
计算 128 * 37 + 99
检索一下 RAG 和长期记忆有什么区别
读取 stage4/README.md
帮我写一条笔记，标题是 tool calling，内容是工具调用让模型可以借助程序完成任务
```

## 验收问题

- Tool Calling 和普通 Prompt 有什么区别？
- 为什么工具描述很重要？
- 为什么工具需要权限控制？
- 为什么工具返回结果还要再给 LLM 总结？
