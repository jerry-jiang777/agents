import re
from pathlib import Path


PROJECT_ROOT = Path("/home/guixuejiang/ws/agents").resolve()
STAGE5_DIR = PROJECT_ROOT / "stage5"
NOTES_DIR = STAGE5_DIR / "notes"

ALLOWED_READ_EXTENSIONS = {".md", ".txt", ".py", ".json"}
BLOCKED_NAMES = {".env", "id_rsa", "id_ed25519", "tool_logs.jsonl"}
BLOCKED_EXTENSIONS = {".db", ".sqlite", ".sqlite3", ".pem", ".key"}
MAX_READ_BYTES = 20_000
MAX_NOTE_CHARS = 10_000


def resolve_safe_read_path(path):
    candidate = (PROJECT_ROOT / path).resolve()
    if not is_relative_to(candidate, PROJECT_ROOT):
        raise PermissionError("只能读取项目目录 /home/guixuejiang/ws/agents 下的文件")
    if not candidate.is_file():
        raise FileNotFoundError(f"文件不存在：{path}")
    if candidate.name in BLOCKED_NAMES or candidate.suffix.lower() in BLOCKED_EXTENSIONS:
        raise PermissionError("该文件类型或文件名禁止读取")
    if candidate.suffix.lower() not in ALLOWED_READ_EXTENSIONS:
        raise PermissionError(f"只允许读取这些类型：{', '.join(sorted(ALLOWED_READ_EXTENSIONS))}")
    if candidate.stat().st_size > MAX_READ_BYTES:
        raise PermissionError(f"文件过大，最大允许读取 {MAX_READ_BYTES} bytes")
    return candidate


def build_safe_note_path(title):
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    safe_title = sanitize_filename(title)
    if not safe_title:
        raise ValueError("笔记标题不能为空")
    return NOTES_DIR / f"{safe_title}.md"


def validate_note_content(content):
    if not content.strip():
        raise ValueError("笔记内容不能为空")
    if len(content) > MAX_NOTE_CHARS:
        raise ValueError(f"笔记内容过长，最大允许 {MAX_NOTE_CHARS} 字符")


def sanitize_filename(value):
    value = value.strip().lower()
    value = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", value)
    value = value.strip(".-_")
    return value[:80]


def is_relative_to(path, base):
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False
