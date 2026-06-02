# Stage 3: 长期记忆与用户画像

本阶段目标：理解长期记忆是跨会话持久化的信息管理系统，不是简单保存所有聊天记录。

## 核心概念

```text
短期记忆 = 当前会话里模型可见的信息
长期记忆 = 跨会话保存、经过筛选、可检索和可删除的有用信息
```

长期记忆应该保存长期有用的信息，例如：

- 用户事实：用户熟悉 Python、正在学习 Agent 系统。
- 用户偏好：用户喜欢结构化、例子多的解释。
- 项目背景：用户正在构建 Agent 学习项目。
- 经验记忆：用户之前使用火山方舟和 OpenAI SDK。
- 任务状态：某个长期项目已经完成到第几步。

长期记忆不应该保存所有聊天记录，也不应该保存 API Key、密码、身份证、手机号等敏感信息。

## 项目文件

```text
stage3/
├── README.md
├── long_memory_chatbot.py
├── memory_store.py
└── memory_extractor.py
```

运行后会自动创建 SQLite 数据库：

```text
stage3/memories.db
```

## 运行方式

先确保已安装 OpenAI SDK：

```bash
pip install openai
```

并设置环境变量：

```bash
export APIKey="你的火山方舟 API Key"
```

运行：

```bash
python long_memory_chatbot.py
```

## CLI 命令

| 命令 | 说明 |
|---|---|
| `/help` | 查看帮助 |
| `/memories` | 查看所有长期记忆 |
| `/remember <type> <content>` | 手动保存一条长期记忆 |
| `/forget <id>` | 删除指定记忆 |
| `/memory_on` | 开启自动记忆提取 |
| `/memory_off` | 关闭自动记忆提取 |
| `/clear` | 清空当前短期上下文 |
| `quit` / `exit` / `退出` | 退出程序 |

可用 memory_type：

```text
user_fact
user_preference
project_context
experience
task_state
```

## 每轮对话流程

```text
用户输入
↓
检索相关长期记忆
↓
组装 prompt：system prompt + 长期记忆 + 短期上下文 + 当前问题
↓
调用模型回答
↓
保存最近短期对话
↓
让 LLM 判断是否有值得长期保存的新记忆
↓
写入 SQLite
```

## 验收问题

完成本阶段后，你应该能解释：

- 长期记忆和短期记忆的区别是什么？
- 长期记忆和聊天记录的区别是什么？
- 为什么长期记忆需要更新和遗忘？
- 为什么长期记忆涉及隐私和权限？
- 为什么不能把所有记忆都塞进 prompt？
