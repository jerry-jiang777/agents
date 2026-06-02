import json
import sys
from pathlib import Path


PROJECT_ROOT = Path("/home/guixuejiang/ws/agents").resolve()
STAGE5_DIR = PROJECT_ROOT / "stage5"
ALLOWED_TOOLS = {
    "calculator",
    "get_current_time",
    "search_docs",
    "read_file",
    "write_note",
    "list_files",
}


def execute_agent_tool(tool_name, action_input):
    if tool_name not in ALLOWED_TOOLS:
        return {"ok": False, "error": f"工具不在白名单中：{tool_name}"}
    if tool_name == "none":
        return {"ok": True, "result": "no action"}
    if tool_name == "list_files":
        return list_files(**(action_input or {}))

    ensure_stage5_import_path()
    from tool_executor import execute_tool

    return execute_tool(tool_name, action_input or {})


def list_files(path=".", max_entries=80):
    target = (PROJECT_ROOT / path).resolve()
    if not is_relative_to(target, PROJECT_ROOT):
        return {"ok": False, "error": "只能列出项目目录下的文件"}
    if not target.exists():
        return {"ok": False, "error": f"路径不存在：{path}"}
    if not target.is_dir():
        return {"ok": False, "error": f"不是目录：{path}"}

    ignored = {".git", "__pycache__", ".venv", "venv"}
    entries = []
    for item in sorted(target.iterdir(), key=lambda value: (not value.is_dir(), value.name.lower())):
        if item.name in ignored:
            continue
        entry_type = "dir" if item.is_dir() else "file"
        entries.append(
            {
                "name": item.name + ("/" if item.is_dir() else ""),
                "type": entry_type,
                "path": str(item.relative_to(PROJECT_ROOT)),
            }
        )
        if len(entries) >= int(max_entries):
            break
    return {"ok": True, "path": str(target.relative_to(PROJECT_ROOT)), "entries": entries}


def observation_preview(observation, max_chars=1600):
    text = json.dumps(observation, ensure_ascii=False)
    if len(text) <= max_chars:
        return observation
    return {"ok": observation.get("ok", True), "preview": text[:max_chars] + "..."}


def ensure_stage5_import_path():
    stage5_path = str(STAGE5_DIR)
    if stage5_path not in sys.path:
        sys.path.insert(0, stage5_path)


def is_relative_to(path, base):
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False
