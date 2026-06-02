from dataclasses import dataclass
from pathlib import Path

import yaml


SKILLS_DIR = Path(__file__).with_name("skills")


@dataclass
class Skill:
    name: str
    version: str
    description: str
    triggers: list
    inputs: list
    steps: list
    tools: list
    outputs: list
    constraints: list
    examples: list
    raw: dict

    def summary(self):
        return f"{self.name} v{self.version}: {self.description.strip()}"

    def to_prompt_text(self):
        return yaml.safe_dump(self.raw, allow_unicode=True, sort_keys=False)


class SkillRegistry:
    def __init__(self, skills_dir=SKILLS_DIR):
        self.skills_dir = Path(skills_dir)
        self.skills = self.load_skills()

    def load_skills(self):
        skills = {}
        for path in sorted(self.skills_dir.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            skill = Skill(
                name=data["name"],
                version=str(data.get("version", "0.0.0")),
                description=data.get("description", ""),
                triggers=data.get("triggers", []),
                inputs=data.get("inputs", []),
                steps=data.get("steps", []),
                tools=data.get("tools", []),
                outputs=data.get("outputs", []),
                constraints=data.get("constraints", []),
                examples=data.get("examples", []),
                raw=data,
            )
            skills[skill.name] = skill
        return skills

    def list_skills(self):
        return list(self.skills.values())

    def get(self, name):
        return self.skills.get(name)

    def summaries_for_prompt(self):
        return "\n".join(f"- {skill.summary()}" for skill in self.list_skills())
