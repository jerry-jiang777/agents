import json
import os

from openai import OpenAI

from agent_logger import log_event, save_run
from agent_prompts import build_decision_messages, build_final_messages, build_plan_messages
from agent_state import AgentState
from tools_adapter import execute_agent_tool, observation_preview


MODEL = "ep-20260525103710-jgg4p"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MAX_STEPS = 8
MAX_ERRORS = 3
MAX_REPEATED_ACTIONS = 2


class MiniAgent:
    def __init__(self, max_steps=MAX_STEPS):
        self.client = build_client()
        self.max_steps = max_steps

    def run(self, goal):
        state = AgentState(goal=goal)
        log_event("run_started", {"goal": goal})
        state.plan = self.generate_plan(goal)
        print("\n[Plan]")
        for index, step in enumerate(state.plan, start=1):
            print(f"{index}. {step}")
        log_event("plan_generated", {"goal": goal, "plan": state.plan})

        finish_reason = "max_steps"
        for _ in range(self.max_steps):
            if state.error_count >= MAX_ERRORS:
                finish_reason = "max_errors"
                break

            decision = self.decide_next_action(state)
            thought = decision.get("thought", "")
            action = decision.get("action", "none")
            action_input = decision.get("action_input") or {}

            if decision.get("is_final"):
                state.status = "completed"
                state.final_answer = decision.get("final_answer", "")
                finish_reason = "model_final"
                break

            if state.repeated_action_count(action, action_input) >= MAX_REPEATED_ACTIONS:
                observation = {
                    "ok": False,
                    "error": "检测到重复动作，已阻止继续执行同一工具和参数。",
                }
                state.add_step(thought, action, action_input, observation)
                finish_reason = "repeated_action"
                break

            print(f"\n[Step {len(state.steps) + 1}]")
            print(f"Thought: {thought}")
            print(f"Action: {action}")
            print(f"Action Input: {json.dumps(action_input, ensure_ascii=False)}")

            observation = execute_agent_tool(action, action_input)
            compact_observation = observation_preview(observation)
            print(f"Observation: {json.dumps(compact_observation, ensure_ascii=False)}")

            state.add_step(thought, action, action_input, compact_observation)
            log_event(
                "step_finished",
                {
                    "goal": state.goal,
                    "step": state.steps[-1],
                    "error_count": state.error_count,
                },
            )
        else:
            finish_reason = "max_steps"

        if not state.final_answer:
            state.final_answer = self.generate_final_answer(state, finish_reason)
            if state.status == "running":
                state.status = "stopped" if finish_reason != "model_final" else "completed"

        run_path = save_run(state)
        log_event(
            "run_finished",
            {
                "goal": state.goal,
                "status": state.status,
                "finish_reason": finish_reason,
                "run_path": str(run_path),
            },
        )
        return state, run_path

    def generate_plan(self, goal):
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=build_plan_messages(goal),
            temperature=0,
        )
        data = parse_json_response(response.choices[0].message.content)
        plan = data.get("plan", [])
        if not isinstance(plan, list) or not plan:
            return ["理解用户目标", "收集必要信息", "基于观察结果输出最终答案"]
        return [str(item) for item in plan[:6]]

    def decide_next_action(self, state):
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=build_decision_messages(state),
            temperature=0,
        )
        try:
            data = parse_json_response(response.choices[0].message.content)
        except ValueError as exc:
            return {
                "thought": f"上一次决策输出不是合法 JSON：{exc}",
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

    def generate_final_answer(self, state, reason):
        response = self.client.chat.completions.create(
            model=MODEL,
            messages=build_final_messages(state, reason),
            temperature=0,
        )
        return response.choices[0].message.content.strip()


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
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"无法解析 JSON：{text}") from exc
