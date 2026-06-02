import json

from memory_store import VALID_MEMORY_TYPES


EXTRACTOR_SYSTEM_PROMPT = """
你是一个长期记忆提取器。你的任务是判断一轮对话中是否有值得长期保存的信息。

值得保存的信息包括：
- 用户长期偏好
- 用户稳定背景
- 项目背景
- 长期任务状态
- 未来可能复用的重要事实或经验

不应保存：
- 寒暄和礼貌用语
- 一次性问题
- 临时情绪
- API Key、密码、身份证、手机号、住址等敏感信息
- 不确定、含糊或可能误解的信息

请只输出合法 JSON，不要输出 Markdown，不要使用代码块。
""".strip()


def extract_memories(client, model, user_input, assistant_output):
    prompt = f"""
请分析下面这轮对话，判断是否包含值得长期保存的记忆。

输出格式必须是合法 JSON：
{{
  "memories": [
    {{
      "should_save": true,
      "memory_type": "user_fact | user_preference | project_context | experience | task_state",
      "content": "一条完整、独立、简洁的中文记忆",
      "confidence": 0.0,
      "privacy_level": "low | medium | high",
      "reason": "保存原因"
    }}
  ]
}}

如果没有值得保存的记忆，请输出：
{{"memories": []}}

用户输入：
{user_input}

助手回答：
{assistant_output}
""".strip()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": EXTRACTOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    text = response.choices[0].message.content.strip()
    return parse_extracted_memories(text)


def parse_extracted_memories(text):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    memories = data.get("memories", [])
    if not isinstance(memories, list):
        return []

    valid_memories = []
    for memory in memories:
        if not isinstance(memory, dict):
            continue
        if not memory.get("should_save"):
            continue

        memory_type = str(memory.get("memory_type", "")).strip()
        content = str(memory.get("content", "")).strip()
        privacy_level = str(memory.get("privacy_level", "medium")).strip().lower()

        try:
            confidence = float(memory.get("confidence", 0))
        except (TypeError, ValueError):
            confidence = 0

        if memory_type not in VALID_MEMORY_TYPES:
            continue
        if not content:
            continue
        if confidence < 0.7:
            continue
        if privacy_level == "high":
            continue

        valid_memories.append(
            {
                "memory_type": memory_type,
                "content": content,
                "confidence": confidence,
                "privacy_level": privacy_level,
                "reason": str(memory.get("reason", "")).strip(),
            }
        )
    return valid_memories
