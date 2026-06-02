from agent_loop import MiniAgent


def print_help():
    print(
        """
可用命令：
/help          查看帮助
/run <goal>    执行一个 Agent 目标
quit/exit/退出 退出程序

示例：
/run 分析 stage5 项目是否实现了工具调用日志。
/run 总结 stage4 RAG 项目的主要模块和作用。
/run 检查 stage6 当前目录有哪些文件，并说明每个文件的职责。
""".strip()
    )


def main():
    print("Mini Agent 执行器已启动。输入 /help 查看帮助。")
    agent = MiniAgent()

    while True:
        user_input = input("\nAgent> ").strip()
        if not user_input:
            continue
        command = user_input.lower()
        if command in ["quit", "exit", "退出"]:
            print("已退出。")
            break
        if command == "/help":
            print_help()
            continue
        if command.startswith("/run "):
            goal = user_input.split(maxsplit=1)[1]
        else:
            goal = user_input

        try:
            state, run_path = agent.run(goal)
        except Exception as exc:
            print(f"执行失败：{exc}")
            continue

        print("\n[Final Answer]")
        print(state.final_answer)
        print(f"\n执行日志已保存：{run_path}")


if __name__ == "__main__":
    main()
