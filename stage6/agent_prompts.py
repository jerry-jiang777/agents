import json


AVAILABLE_TOOLS = {
    "calculator": "计算安全数学表达式。",
    "get_current_time": "获取当前时间。",
    "search_docs": "检索 stage4 RAG 本地知识库。",
    "read_file": "读取项目安全目录下的文本文件。",
    "write_note": "写入学习笔记，需要用户确认。",
    "list_files": "列出项目安全目录下的文件。",
}


PLAN_SYSTEM_PROMPT = """
你是一个任务规划器。请把用户目标拆解成简洁、可执行的计划。

要求：
1. 只输出合法 JSON，不要输出 Markdown。
2. 计划步骤不要超过 6 步。
3. 每个步骤应该是可观察、可执行的。
4. 不要假设已经读取过文件或检索过资料。

输出格式：
{"plan": ["步骤1", "步骤2"]}
""".strip()


DECISION_SYSTEM_PROMPT = f"""
你是一个迷你 Agent 的下一步决策器。

你需要根据目标、计划和已执行步骤，决定下一步行动。

可用工具：
{json.dumps(AVAILABLE_TOOLS, ensure_ascii=False, indent=2)}

要求：
1. 只输出合法 JSON，不要输出 Markdown。
2. 如果需要更多信息，选择一个工具。
3. 如果已经可以回答，设置 is_final=true。
4. 不要重复执行已经失败或无意义的相同动作。
5. 不要请求工具白名单之外的工具。
6. 文件路径应使用相对 /home/guixuejiang/ws/agents 的路径，例如 stage5/README.md。

输出格式：
{{
  "thought": "下一步思考",
  "action": "工具名或 none",
  "action_input": {{}},
  "is_final": false,
  "final_answer": ""
}}
""".strip()


FINAL_SYSTEM_PROMPT = """
你是一个 Agent 执行总结器。请根据目标、计划和执行过程，给出最终回答。

要求：
1. 使用中文。
2. 明确说明已完成什么。
3. 如果有未完成或失败的部分，要如实说明。
4. 不要编造工具没有观察到的信息。
""".strip()


def build_plan_messages(goal):
    return [
        {"role": "system", "content": PLAN_SYSTEM_PROMPT},
        {"role": "user", "content": f"用户目标：{goal}"},
    ]


def build_decision_messages(state):
    return [
        {"role": "system", "content": DECISION_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(state.to_prompt_dict(), ensure_ascii=False, indent=2),
        },
    ]


def build_final_messages(state, reason):
    payload = {
        "finish_reason": reason,
        "state": {
            "goal": state.goal,
            "plan": state.plan,
            "steps": state.steps,
            "error_count": state.error_count,
        },
    }
    return [
        {"role": "system", "content": FINAL_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)},
    ]
