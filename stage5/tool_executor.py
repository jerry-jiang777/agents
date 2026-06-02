import json

from tool_logger import log_tool_call
from tools import calculator, get_current_time, read_file, search_docs, write_note


TOOL_FUNCTIONS = {
    "calculator": calculator,
    "get_current_time": get_current_time,
    "search_docs": search_docs,
    "read_file": read_file,
    "write_note": write_note,
}

SENSITIVE_TOOLS = {"write_note"}


def execute_tool(tool_name, arguments):
    arguments = arguments or {}
    if tool_name not in TOOL_FUNCTIONS:
        result = {"ok": False, "error": f"未知工具：{tool_name}"}
        log_tool_call(tool_name, arguments, result)
        return result

    if tool_name in SENSITIVE_TOOLS and not confirm_sensitive_tool(tool_name, arguments):
        result = {"ok": False, "error": "用户取消了敏感工具调用"}
        log_tool_call(tool_name, arguments, result)
        return result

    try:
        result = TOOL_FUNCTIONS[tool_name](**arguments)
    except Exception as exc:
        result = {"ok": False, "error": str(exc)}

    log_tool_call(tool_name, arguments, result)
    return result


def parse_tool_arguments(raw_arguments):
    if not raw_arguments:
        return {}
    try:
        data = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        raise ValueError(f"工具参数不是合法 JSON：{exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("工具参数必须是 JSON object")
    return data


def tool_result_to_json(result):
    return json.dumps(result, ensure_ascii=False)


def confirm_sensitive_tool(tool_name, arguments):
    print(f"\n[权限确认] 模型请求执行敏感工具：{tool_name}")
    print(json.dumps(arguments, ensure_ascii=False, indent=2))
    answer = input("是否允许执行？输入 y 确认，其它输入取消：").strip().lower()
    return answer == "y"
