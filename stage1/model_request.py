import os
import time
from openai import OpenAI



# 1.初始化客户端apikey放到环境变量中防止泄露
api_key = os.getenv("APIKey")
print(f"api_key = {api_key}")
client = OpenAI(api_key = api_key, base_url="https://ark.cn-beijing.volces.com/api/v3")

# 2.初始化消息列表并设定System prompt
messages = [
    {"role": "system", "content": "你是一个严谨且乐于助人的AI助手。回答要简洁准确。"}
]

print("CLI聊天机器人已启动(输入'quit'或'exit'退出)")


while True:
    # 3.获取用户输入
    user_input = input("\n User:")
    # 支持用户输入是否为退出指令
    if user_input.lower() in ['quit', 'exit', '退出']:
        print("聊天机器人已退出")
        break

    # 4.将用户输入添加到消息列表中
    messages.append({"role": "user", "content": user_input})


    try:
        print("AI:", end=" ", flush=True)
        start_time = time.time()
        full_response = ""


        #5.调用LLM API（开启历史输出 stream=True）
        # 工程化细节：设置temprature=0，保证回答严谨，设置max_tokens 防止生成过长
        response = client.chat.completions.create(
            model="ep-20260525103710-jgg4p",
            messages=messages,
            temperature=0,
            stream=True,# 开启流式输出（开启打印机效果）
            max_tokens=2048
        )

        # 6.处理流式输出
        for chunk in response:
            # print(chunk)
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)#实时打印 
                full_response += content
        # 7.将AI的完整回答添加到消息列表中（实现多轮对话的关键）
        messages.append({"role": "assistant", "content": full_response})

        #8.打印统计信息（响应时间和Token使用量）
        end_time = time.time()
        # 注意：流式输出时，useage信息通常在最后一个chunk中或者单独获取，这里简化展示
        print(f"\n\n---统计：耗时    {end_time - start_time:.2f}s | 当前对话总轮数：{(len(messages)-1) // 2}---")


    except Exception as e:
        #9.错误处理(工程化细节：错误捕获与重试提示)
        print(f"\n发生错误：{e}")
        print(f"请检查网络连接或API Key是否正确，并重试。")
        # 如果是因为上下文超长导致的错误，可以在这里加入“截断历史消息”的逻辑