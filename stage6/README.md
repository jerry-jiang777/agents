# Stage 6: Agent 规划与执行循环

本阶段目标：理解 Agent 的本质：围绕目标进行多步规划、工具调用、观察反馈和迭代执行。

## 核心流程

```text
用户目标
↓
LLM 生成初始计划
↓
LLM 根据状态决定下一步
↓
选择工具并执行
↓
记录 Observation
↓
判断是否完成
↓
未完成则继续
↓
输出最终答案
```

## 经典结构

```text
Thought：我需要做什么
Action：我要调用哪个工具
Action Input：工具参数
Observation：工具返回了什么
Final Answer：最终回答
```

## 项目结构

```text
stage6/
├── README.md
├── mini_agent.py
├── agent_state.py
├── agent_prompts.py
├── agent_loop.py
├── tools_adapter.py
├── agent_logger.py
├── agent_logs.jsonl
└── runs/
```

## 保护机制

- 最大执行步数：防止无限循环。
- 最大错误次数：防止反复失败。
- 重复动作检测：防止一直调用同一个工具和参数。
- 工具白名单：只允许安全工具。
- 写入工具确认：复用 Stage 5 的 `write_note` 用户确认机制。
- 执行日志：记录每一步 Thought/Action/Observation。

## 可用工具

复用 Stage 5：

- `calculator`
- `get_current_time`
- `search_docs`
- `read_file`
- `write_note`

Stage 6 新增：

- `list_files`

## 运行方式

设置火山方舟 API Key：

```bash
export APIKey="你的火山方舟 API Key"
```

运行：

```bash
cd /home/guixuejiang/ws/agents/stage6
python mini_agent.py
```

## 测试目标

```text
分析 stage5 项目是否实现了工具调用日志。
```

```text
总结 stage4 RAG 项目的主要模块和作用。
```

```text
检查 stage6 当前目录有哪些文件，并说明每个文件的职责。
```

## 验收问题

- Agent 和 Chatbot 的本质区别是什么？
- Agent 和 RAG 的区别是什么？
- 为什么 Agent 需要工具？
- 为什么 Agent 需要状态管理？
- 为什么 Agent 需要终止条件？
- 为什么 Agent 容易失控？
