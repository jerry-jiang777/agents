import json
import os

from openai import OpenAI


MODEL = "ep-20260525103710-jgg4p"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MIN_CONFIDENCE = 0.6


SELECTOR_SYSTEM_PROMPT = """
你是 Skill 选择器。

请根据用户目标，从可用 Skill 中选择最合适的一个。
如果没有合适 Skill，返回 none。

要求：
1. 只输出合法 JSON，不要输出 Markdown。
2. confidence 范围是 0 到 1。
3. 如果用户目标明显属于某个 Skill，confidence 应大于 0.8。

输出格式：
{
  "skill_name": "learning_note | competitor_analysis | prd_draft | none",
  "confidence": 0.0,
  "reason": "选择原因"
}
""".strip()


class SkillSelector:
    def __init__(self):
        self.client = build_client()

    def select(self, goal, registry):
        user_prompt = f"""
用户目标：
{goal}

可用 Skill：
{registry.summaries_for_prompt()}
""".strip()
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SELECTOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,
        )
        data = parse_json_response(response.choices[0].message.content)
        skill_name = data.get("skill_name", "none")
        confidence = float(data.get("confidence", 0))
        if confidence < MIN_CONFIDENCE:
            skill_name = "none"
        return {
            "skill_name": skill_name,
            "confidence": confidence,
            "reason": data.get("reason", ""),
        }


def build_client():
    api_key = os.getenv("APIKey")
    if not api_key:
        raise RuntimeError("请先设置环境变量 APIKey")
    return OpenAI(api_key=api_key, base_url=BASE_URL)


def parse_json_response(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
        if text.startswith("json"):
            text = text[4:].strip()
    return json.loads(text)
