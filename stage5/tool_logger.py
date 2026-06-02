import json
from datetime import datetime, timezone
from pathlib import Path


LOG_PATH = Path(__file__).with_name("tool_logs.jsonl")


def log_tool_call(tool_name, arguments, result):
    record = {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool_name": tool_name,
        "arguments": arguments,
        "ok": bool(result.get("ok")),
        "result_preview": build_preview(result),
    }
    with LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_preview(result, max_chars=300):
    text = json.dumps(result, ensure_ascii=False)
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
