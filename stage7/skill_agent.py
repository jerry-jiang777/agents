from skill_executor import SkillExecutor
from skill_registry import SkillRegistry
from skill_selector import SkillSelector


def print_help():
    print(
        """
可用命令：
/help                         查看帮助
/skills                       列出所有 Skill
/show_skill <name>            查看 Skill 定义
/use <skill_name> <goal>      手动指定 Skill 执行
/run <goal>                   自动选择 Skill 后执行
quit / exit / 退出             退出程序

示例：
/skills
/show_skill learning_note
/use learning_note 帮我整理第 6 阶段 Agent 的学习笔记
/run 帮我写一个学习计划管理功能的 PRD 草稿
""".strip()
    )


def main():
    registry = SkillRegistry()
    selector = SkillSelector()
    executor = SkillExecutor()

    print("Skill Agent 已启动。输入 /help 查看帮助。")

    while True:
        user_input = input("\nSkillAgent> ").strip()
        if not user_input:
            continue

        command = user_input.lower()
        if command in ["quit", "exit", "退出"]:
            print("已退出。")
            break
        if command == "/help":
            print_help()
            continue
        if command == "/skills":
            for skill in registry.list_skills():
                print(f"- {skill.summary()}")
            continue
        if command.startswith("/show_skill "):
            name = user_input.split(maxsplit=1)[1].strip()
            skill = registry.get(name)
            if not skill:
                print(f"未找到 Skill：{name}")
                continue
            print(skill.to_prompt_text())
            continue
        if command.startswith("/use "):
            parts = user_input.split(maxsplit=2)
            if len(parts) < 3:
                print("用法：/use <skill_name> <goal>")
                continue
            skill_name = parts[1]
            goal = parts[2]
            skill = registry.get(skill_name)
            if not skill:
                print(f"未找到 Skill：{skill_name}")
                continue
            run_goal(executor, goal, skill)
            continue
        if command.startswith("/run "):
            goal = user_input.split(maxsplit=1)[1]
        else:
            goal = user_input

        try:
            selection = selector.select(goal, registry)
        except Exception as exc:
            print(f"自动选择 Skill 失败，将使用普通 Agent 模式：{exc}")
            selection = {"skill_name": "none", "confidence": 0, "reason": "selector failed"}

        skill = registry.get(selection["skill_name"])
        print(
            f"[Skill Selector] skill={selection['skill_name']} "
            f"confidence={selection['confidence']:.2f} reason={selection['reason']}"
        )
        run_goal(executor, goal, skill)


def run_goal(executor, goal, skill):
    try:
        result, run_path = executor.run(goal, skill)
    except Exception as exc:
        print(f"执行失败：{exc}")
        return

    print("\n[Final Answer]")
    print(result["final_answer"])
    print(f"\n执行日志已保存：{run_path}")


if __name__ == "__main__":
    main()
