import os

from openai import OpenAI

from memory_extractor import extract_memories
from memory_store import (
    VALID_MEMORY_TYPES,
    add_memory,
    delete_memory,
    init_db,
    list_memories,
    mark_memories_used,
    search_memories,
)


MODEL = "ep-20260525103710-jgg4p"
USER_ID = "default_user"
MAX_RECENT_TURNS = 6
SYSTEM_PROMPT = """
你是一个严谨且乐于助人的 AI 助手。
回答要求：
1. 使用中文。
2. 先直接回答问题，再补充必要解释。
3. 可以参考长期记忆调整回答方式，但不要机械复述记忆内容。
4. 不要编造用户没有提供过的信息。
""".strip()


def build_client():
    api_key = os.getenv("APIKey")
    if not api_key:
        raise RuntimeError("请先设置环境变量 APIKey")
    return OpenAI(api_key=api_key, base_url="https://ark.cn-beijing.volces.com/api/v3")


def format_memory_block(memories):
    if not memories:
        return "暂无相关长期记忆。"
    return "\n".join(
        f"- [{memory['id']}] {memory['memory_type']}: {memory['content']}"
        for memory in memories
    )


def build_messages(user_input, recent_messages, related_memories):
    memory_block = format_memory_block(related_memories)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": f"以下是与用户相关的长期记忆，请作为背景参考，不要直接泄露：\n{memory_block}",
        },
    ]
    messages.extend(recent_messages)
    messages.append({"role": "user", "content": user_input})
    return messages


def print_help():
    print(
        """
可用命令：
/help                         查看帮助
/memories                     查看所有长期记忆
/remember <type> <content>    手动保存一条长期记忆
/forget <id>                  删除指定长期记忆
/memory_on                    开启自动记忆提取
/memory_off                   关闭自动记忆提取
/clear                        清空当前短期上下文
quit / exit / 退出             退出程序

可用 type：
user_fact, user_preference, project_context, experience, task_state
""".strip()
    )


def print_memories():
    memories = list_memories(USER_ID)
    if not memories:
        print("暂无长期记忆。")
        return

    print("\n---长期记忆---")
    for memory in memories:
        print(
            f"[{memory['id']}] {memory['memory_type']} "
            f"confidence={memory['confidence']:.2f} source={memory['source']}\n"
            f"    {memory['content']}"
        )


def handle_remember_command(command):
    parts = command.split(maxsplit=2)
    if len(parts) < 3:
        print("用法：/remember <type> <content>")
        return

    memory_type = parts[1].strip()
    content = parts[2].strip()
    if memory_type not in VALID_MEMORY_TYPES:
        print(f"无效 type。可用 type：{', '.join(sorted(VALID_MEMORY_TYPES))}")
        return

    memory_id = add_memory(USER_ID, memory_type, content, confidence=1.0, source="manual")
    print(f"已保存长期记忆：[{memory_id}] {memory_type}: {content}")


def handle_forget_command(command):
    parts = command.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        print("用法：/forget <id>")
        return

    memory_id = int(parts[1].strip())
    if delete_memory(USER_ID, memory_id):
        print(f"已删除长期记忆：{memory_id}")
    else:
        print(f"未找到可删除的长期记忆：{memory_id}")


def main():
    init_db()
    client = build_client()
    recent_messages = []
    auto_memory_enabled = True

    print("长期记忆聊天机器人已启动。输入 /help 查看命令。")

    while True:
        user_input = input("\nUser: ").strip()
        if not user_input:
            continue

        command = user_input.lower()
        if command in ["quit", "exit", "退出"]:
            print("聊天机器人已退出。")
            break
        if command == "/help":
            print_help()
            continue
        if command == "/memories":
            print_memories()
            continue
        if command.startswith("/remember "):
            handle_remember_command(user_input)
            continue
        if command.startswith("/forget "):
            handle_forget_command(user_input)
            continue
        if command == "/memory_on":
            auto_memory_enabled = True
            print("自动记忆提取已开启。")
            continue
        if command == "/memory_off":
            auto_memory_enabled = False
            print("自动记忆提取已关闭。")
            continue
        if command == "/clear":
            recent_messages.clear()
            print("短期上下文已清空，长期记忆不受影响。")
            continue

        related_memories = search_memories(USER_ID, user_input)
        mark_memories_used(USER_ID, [memory["id"] for memory in related_memories])
        messages = build_messages(user_input, recent_messages, related_memories)

        print("AI: ", end="", flush=True)
        full_response = ""
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        print()

        recent_messages.append({"role": "user", "content": user_input})
        recent_messages.append({"role": "assistant", "content": full_response})
        recent_messages = recent_messages[-(MAX_RECENT_TURNS * 2):]

        if auto_memory_enabled:
            try:
                extracted_memories = extract_memories(client, MODEL, user_input, full_response)
            except Exception as exc:
                print(f"[系统] 自动记忆提取失败：{exc}")
                continue

            for memory in extracted_memories:
                memory_id = add_memory(
                    USER_ID,
                    memory["memory_type"],
                    memory["content"],
                    confidence=memory["confidence"],
                    source="chat_extraction",
                )
                print(f"[系统] 已保存长期记忆：[{memory_id}] {memory['memory_type']}: {memory['content']}")


if __name__ == "__main__":
    main()
