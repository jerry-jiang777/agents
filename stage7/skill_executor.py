import json
import os
import sys
from pathlib import Path

from openai import OpenAI

from skill_logger import log_skill_event, save_skill_run


PROJECT_ROOT = Path("/home/guixuejiang/ws/agents").resolve()
STAGE6_DIR = PROJECT_ROOT / "stage6"
if str(STAGE6_DIR) not in sys.path:
    sys.path.insert(0, str(STAGE6_DIR))

from agent_state import AgentState
from tools_adapter import execute_agent_tool, observation_preview


MODEL = "ep-20260525103710-jgg4p"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MAX_STEPS = 8
MAX_ERRORS = 3
MAX_REPEATED_ACTIONS = 2


class SkillExecutor:
    def __init__(self):
        self.client = build_client()

    def run(self, goal, skill):
        state = AgentState(goal=goal)
        log_skill_event(
            "skill_run_started",
            {
                "goal": goal,
                "skill_name": skill.name if skill else "none",
                "skill_version": skill.version if skill else "none",
            },
        )

        state.plan = self.generate_plan(goal, skill)
        print("\n[Skill]")
        if skill:
            print(f"{skill.name} v{skill.version}")
        else:
            print("none，使用普通 Agent 模式")

        print("\n[Plan]")
        for index, step in enumerate(state.plan, start=1):
            print(f"{index}. {step}")

        finish_reason = "max_steps"
        for _ in range(MAX_STEPS):
            if state.error_count >= MAX_ERRORS:
                finish_reason = "max_errors"
                break

            decision = self.decide_next_action(state, skill)
            thought = decision.get("thought", "")
            action = decision.get("action", "none")
            action_input = decision.get("action_input") or {}

            if decision.get("is_final"):
                state.status = "completed"
                state.final_answer = decision.get("final_answer", "")
                finish_reason = "model_final"
                break

            if skill and action != "none" and action not in skill.tools:
                observation = {
                    "ok": False,
                    "error": f"工具 {action} 不在当前 Skill 允许工具列表中：{skill.tools}",
                }
            elif state.repeated_action_count(action, action_input) >= MAX_REPEATED_ACTIONS:
                observation = {
                    "ok": False,
                    "error": "检测到重复动作，已阻止继续执行同一工具和参数。",
                }
                state.add_step(thought, action, action_input, observation)
                finish_reason = "repeated_action"
                break
            else:
                print(f"\n[Step {len(state.steps) + 1}]")
                print(f"Thought: {thought}")
                print(f"Action: {action}")
                print(f"Action Input: {json.dumps(action_input, ensure_ascii=False)}")
                observation = execute_agent_tool(action, action_input)

            compact_observation = observation_preview(observation)
            print(f"Observation: {json.dumps(compact_observation, ensure_ascii=False)}")
            state.add_step(thought, action, action_input, compact_observation)
            log_skill_event(
                "skill_step_finished",
                {
                    "skill_name": skill.name if skill else "none",
                    "goal": goal,
                    "step": state.steps[-1],
                    "error_count": state.error_count,
                },
            )

        if not state.final_answer:
            state.final_answer = self.generate_final_answer(state, skill, finish_reason)
            state.status = "stopped" if finish_reason != "model_final" else "completed"

        result = {
            "status": state.status,
            "finish_reason": finish_reason,
            "plan": state.plan,
            "steps": state.steps,
            "final_answer": state.final_answer,
            "error_count": state.error_count,
        }
        run_path = save_skill_run(goal, skill, result)
        log_skill_event(
            "skill_run_finished",
            {
                "skill_name": skill.name if skill else "none",
                "goal": goal,
                "status": state.status,
                "finish_reason": finish_reason,
                "run_path": str(run_path),
            },
        )
        return result, run_path

    def generate_plan(self, goal, skill):
        messages = [
            {"role": "system", "content": build_plan_prompt(skill)},
            {"role": "user", "content": f"用户目标：{goal}"},
        ]
        response = self.client.chat.completions.create(model=MODEL, messages=messages, temperature=0)
        data = parse_json_response(response.choices[0].message.content)
        plan = data.get("plan", [])
        if not isinstance(plan, list) or not plan:
            return ["理解用户目标", "收集必要信息", "按要求输出最终结果"]
        return [str(item) for item in plan[:8]]

    def decide_next_action(self, state, skill):
        messages = [
            {"role": "system", "content": build_decision_prompt(skill)},
            {"role": "user", "content": json.dumps(state.to_prompt_dict(), ensure_ascii=False, indent=2)},
        ]
        response = self.client.chat.completions.create(model=MODEL, messages=messages, temperature=0)
        try:
            data = parse_json_response(response.choices[0].message.content)
        except Exception as exc:
            return {
                "thought": f"决策输出解析失败：{exc}",
                "action": "none",
                "action_input": {},
                "is_final": True,
                "final_answer": "Agent 决策输出格式错误，已安全停止。",
            }
        data.setdefault("thought", "")
        data.setdefault("action", "none")
        data.setdefault("action_input", {})
        data.setdefault("is_final", False)
        data.setdefault("final_answer", "")
        if not isinstance(data["action_input"], dict):
            data["action_input"] = {}
        return data

    def generate_final_answer(self, state, skill, reason):
        payload = {
            "finish_reason": reason,
            "skill": None if skill is None else skill.raw,
            "state": {
                "goal": state.goal,
                "plan": state.plan,
                "steps": state.steps,
                "error_count": state.error_count,
            },
        }
        messages = [
            {"role": "system", "content": build_final_prompt(skill)},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)},
        ]
        response = self.client.chat.completions.create(model=MODEL, messages=messages, temperature=0)
        return response.choices[0].message.content.strip()


def build_plan_prompt(skill):
    skill_text = "无 Skill，按普通 Agent 方式规划。" if skill is None else skill.to_prompt_text()
    return f"""
你是一个带 Skill 的任务规划器。

请根据用户目标和当前 Skill，生成简洁、可执行的计划。

当前 Skill：
{skill_text}

要求：
1. 只输出合法 JSON，不要输出 Markdown。
2. 计划应服务于 Skill steps。
3. 不要超过 8 步。
4. 不要假设已经读取过文件或检索过资料。

输出格式：
{{"plan": ["步骤1", "步骤2"]}}
""".strip()


def build_decision_prompt(skill):
    skill_text = "无 Skill，按普通 Agent 模式执行。" if skill is None else skill.to_prompt_text()
    allowed_tools = ["calculator", "get_current_time", "search_docs", "read_file", "write_note", "list_files"]
    if skill is not None:
        allowed_tools = skill.tools
    return f"""
你是一个带 Skill 的 Agent 下一步决策器。

当前 Skill：
{skill_text}

允许工具：
{json.dumps(allowed_tools, ensure_ascii=False)}

要求：
1. 只输出合法 JSON，不要输出 Markdown。
2. 下一步行动必须服务于 Skill steps。
3. 不得违反 Skill constraints。
4. 最终输出必须符合 Skill outputs。
5. 只能使用允许工具，或者 action=none。
6. 如果已经足够回答，设置 is_final=true。
7. 不要重复执行已经失败或无意义的同一动作。

输出格式：
{{
  "thought": "下一步思考",
  "action": "工具名或 none",
  "action_input": {{}},
  "is_final": false,
  "final_answer": ""
}}
""".strip()


def build_final_prompt(skill):
    skill_text = "无 Skill。" if skill is None else skill.to_prompt_text()
    return f"""
你是一个带 Skill 的 Agent 执行总结器。

当前 Skill：
{skill_text}

要求：
1. 使用中文。
2. 按 Skill outputs 的格式组织最终结果。
3. 明确说明已完成什么。
4. 如果资料不足、工具失败或存在不确定信息，要如实说明。
5. 不要编造工具没有观察到的信息。
""".strip()


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
