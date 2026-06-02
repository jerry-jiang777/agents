from dataclasses import dataclass, field


@dataclass
class AgentState:
    goal: str
    plan: list[str] = field(default_factory=list)
    steps: list[dict] = field(default_factory=list)
    status: str = "running"
    final_answer: str = ""
    error_count: int = 0

    def add_step(self, thought, action, action_input, observation):
        self.steps.append(
            {
                "step": len(self.steps) + 1,
                "thought": thought,
                "action": action,
                "action_input": action_input,
                "observation": observation,
            }
        )
        if isinstance(observation, dict) and not observation.get("ok", True):
            self.error_count += 1

    def recent_steps(self, limit=6):
        return self.steps[-limit:]

    def repeated_action_count(self, action, action_input):
        count = 0
        for step in reversed(self.steps):
            if step["action"] == action and step["action_input"] == action_input:
                count += 1
            else:
                break
        return count

    def to_prompt_dict(self):
        return {
            "goal": self.goal,
            "plan": self.plan,
            "status": self.status,
            "error_count": self.error_count,
            "recent_steps": self.recent_steps(),
        }
