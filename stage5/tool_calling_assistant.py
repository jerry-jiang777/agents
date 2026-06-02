import os

from openai import OpenAI

from tool_executor import execute_tool, parse_tool_arguments, tool_result_to_json
from tool_schemas import TOOLS


MODEL = "ep-20260525103710-jgg4p"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MAX_RECENT_MESSAGES = 20
SYSTEM_PROMPT = """
你是一个支持工具调用的 AI 助手。

原则：
1. 用户要求计算、查时间、检索本地知识库、读取项目文件、写学习笔记时，优先调用合适工具。
2. 工具失败时，基于工具错误向用户解释原因，不要假装成功。
3. 不要声称你直接执行了系统命令。
4. 对工具结果进行清晰总结，必要时说明来源或下一步建议。
5. 使用中文回答。
""".strip()


def build_client():
    api_key = os.getenv("APIKey")
    if not api_key:
        raise RuntimeError("请先设置环境变量 APIKey")
    return OpenAI(api_key=api_key, base_url=BASE_URL)


def print_help():
    print(
        """
可用命令：
/help          查看帮助
/tools         查看可用工具
/clear         清空短期上下文
quit/exit/退出 退出程序

示例：
现在几点？
计算 128 * 37 + 99
检索一下 RAG 和长期记忆有什么区别
读取 stage4/README.md
帮我写一条笔记，标题是 tool calling，内容是工具调用让模型可以借助程序完成任务
""".strip()
    )


def print_tools():
    print("可用工具：")
    for tool in TOOLS:
        function = tool["function"]
        print(f"- {function['name']}: {function['description']}")


def main():
    client = build_client()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Tool Calling AI 助手已启动。输入 /help 查看帮助。")

    while True:
        user_input = input("\nUser: ").strip()
        if not user_input:
            continue

        command = user_input.lower()
        if command in ["quit", "exit", "退出"]:
            print("已退出。")
            break
        if command == "/help":
            print_help()
            continue
        if command == "/tools":
            print_tools()
            continue
        if command == "/clear":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("短期上下文已清空。")
            continue

        messages.append({"role": "user", "content": user_input})
        try:
            messages = run_turn(client, messages)
        except Exception as exc:
            print(f"发生错误：{exc}")

        messages = [messages[0]] + messages[-MAX_RECENT_MESSAGES:]


def run_turn(client, messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )
    assistant_message = response.choices[0].message
    messages.append(assistant_message)

    tool_calls = assistant_message.tool_calls or []
    if not tool_calls:
        print(f"AI: {assistant_message.content}")
        return messages

    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        try:
            arguments = parse_tool_arguments(tool_call.function.arguments)
        except Exception as exc:
            result = {"ok": False, "error": str(exc)}
        else:
            print(f"[工具调用] {tool_name}({arguments})")
            result = execute_tool(tool_name, arguments)
        print(f"[工具结果] {tool_result_to_json(result)}")

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": tool_result_to_json(result),
            }
        )

    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    final_message = final_response.choices[0].message
    messages.append(final_message)
    print(f"AI: {final_message.content}")
    return messages


if __name__ == "__main__":
    main()
