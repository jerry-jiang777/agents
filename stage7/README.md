# Stage 7: Skill 能力封装

本阶段目标：理解 Skill 是对高频任务能力的沉淀，不是单个工具。

## 核心概念

```text
Tool 是动作
Skill 是方法
```

例如：

```text
Tool：read_file、search_docs、write_note
Skill：学习笔记、竞品分析、PRD 草稿
```

Skill 通常包含：

- 名称和版本
- 触发条件
- 输入说明
- 执行步骤
- 可使用工具
- 输出格式
- 执行约束
- 示例

## 项目结构

```text
stage7/
├── README.md
├── skill_agent.py
├── skill_registry.py
├── skill_selector.py
├── skill_executor.py
├── skill_logger.py
├── skills/
│   ├── learning_note.yaml
│   ├── competitor_analysis.yaml
│   └── prd_draft.yaml
├── runs/
└── skill_logs.jsonl
```

## 运行方式

安装依赖：

```bash
pip install pyyaml openai
```

设置 API Key：

```bash
export APIKey="你的火山方舟 API Key"
```

运行：

```bash
cd /home/guixuejiang/ws/agents/stage7
python skill_agent.py
```

## CLI 命令

| 命令 | 说明 |
|---|---|
| `/help` | 查看帮助 |
| `/skills` | 列出所有 Skill |
| `/show_skill <name>` | 查看 Skill 定义 |
| `/use <skill_name> <goal>` | 手动指定 Skill 执行 |
| `/run <goal>` | 自动选择 Skill 后执行 |
| `quit` / `exit` / `退出` | 退出程序 |

## 测试任务

```text
/use learning_note 帮我整理第 6 阶段 Agent 的学习笔记
```

```text
/run 帮我写一个学习计划管理功能的 PRD 草稿
```

```text
/use competitor_analysis 基于我提供的信息对比 Notion 和 Obsidian 的学习笔记能力
```

## 验收问题

- 为什么 Skill 不是 Tool？
- 为什么 Skill 可以降低 Agent 随机性？
- 为什么 Skill 适合沉淀领域经验？
- Skill 和 Workflow 有什么相似和不同？
