import os
# import time
from openai import OpenAI


#1.初始化客户端apikey放到环境变量中防止泄露
client = OpenAI(api_key = os.getenv("APIKey"), base_url="https://ark.cn-beijing.volces.com/api/v3")

# 基础配置
SYSTEM_PROMPT = "你是一个严谨且乐于助人的AI助手。"
MAX_RECENT_TURNS = 3 # 只保留最近3轮对话(即6条消息：3个User消息 + 3个assistant消息)
SUMMARY_TRIGGER = 4 # 当总对话轮数超过4轮时，触发总结机制



# 全局状态记录
all_messages = [] # 记录所有对话消息（不受限制）
conversation_summary = "" # 存储早期对话的摘要


def get_context_messages():
    """每次请求前,动态组装最终的prompt"""
    context = [{"role": "system", "content": SYSTEM_PROMPT}]

    # 1.如果有摘要,先放入摘要
    if conversation_summary:
        context.append({"role": "system", "content": f"以下是之前对话的总结：\n{conversation_summary}"})

    # 2.添加最近N轮对话(切片去最后的MAX_RECENT_TURNS*2条消息)
    recent_messages = all_messages[-(MAX_RECENT_TURNS*2):]
    context.extend(recent_messages)


    return context


def format_messages(messages):
    """将消息列表转换为适合摘要模型阅读的文本"""
    return "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages)


def summarize_conversation(old_summary, messages_to_summarize):
    """调用大模型对旧的对话进行压缩总结"""
    print(f"\n[系统]对话过长，正在进行记忆压缩...")
    summary_prompt = [
        {"role": "system", "content": "你是一个对话记忆压缩助手。请把旧摘要和新增历史对话合并为一段新的记忆摘要。"},
        {"role": "user", "content": f"""
请将以下内容压缩成一段简洁、准确的中文记忆摘要，用于后续对话参考。

要求：
1. 保留用户明确表达的目标、偏好、任务进度和关键事实。
2. 保留重要文件名、命令、错误信息、模型接入点等精确信息。
3. 不要加入原文没有的信息。
4. 不要把不确定的信息写成确定事实。
5. 删除寒暄和无关细节。
6. 控制在 300 字以内。

已有摘要：
{old_summary or "无"}

需要新增压缩的历史对话：
{format_messages(messages_to_summarize)}
"""}
    ]


    response = client.chat.completions.create(
        model="ep-20260525103710-jgg4p",
        messages=summary_prompt,
        temperature=0
    )

    return response.choices[0].message.content


def compress_memory_if_needed():
    """超过最近对话保留上限时，将更早的对话压缩进摘要"""
    global all_messages, conversation_summary

    max_recent_messages = MAX_RECENT_TURNS * 2
    total_turns = len(all_messages) // 2
    if total_turns <= SUMMARY_TRIGGER or len(all_messages) <= max_recent_messages:
        return

    old_messages = all_messages[:-max_recent_messages]
    if not old_messages:
        return

    conversation_summary = summarize_conversation(conversation_summary, old_messages)
    all_messages = all_messages[-max_recent_messages:]



print("智能聊天机器人已启动（输入'clear'清空上下文，'memory'查看当前记忆）")

while True:
    user_input = input("\nUser:")
    command = user_input.strip().lower()

    if command in ['quit', 'exit', '退出']:
        print("聊天机器人已退出")
        break

    if command in ['clear', '清空上下文']:
        all_messages.clear()
        conversation_summary = ""
        print("上下文已清空。")
        continue

    if command in ['memory', '查看记忆', '查看当前记忆']:
        print(f"\n---当前记忆摘要---\n{conversation_summary or '暂无摘要'}\n---最近对话---")
        for msg in all_messages[-(MAX_RECENT_TURNS*2):]:
            print(f"{msg['role']}: {msg['content']}")
        continue


    # 将新对话加入全局记录
    all_messages.append({"role": "user", "content": user_input})
    
    # 获取组装好的上下文并调用LLM
    context_messages = get_context_messages()
    print("🤖 AI: ", end="", flush=True)
    full_response = ""
    response = client.chat.completions.create(
        model="ep-20260525103710-jgg4p",
        messages=context_messages,
        stream=True
    )
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_response += content
    all_messages.append({"role": "assistant", "content": full_response})
    compress_memory_if_needed()
