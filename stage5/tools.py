import ast
import operator
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from permissions import build_safe_note_path, resolve_safe_read_path, validate_note_content


PROJECT_ROOT = Path("/home/guixuejiang/ws/agents").resolve()
STAGE4_DIR = PROJECT_ROOT / "stage4"

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def calculator(expression):
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("expression 不能为空")
    if len(expression) > 200:
        raise ValueError("expression 过长")
    tree = ast.parse(expression, mode="eval")
    result = eval_math_node(tree.body)
    return {"ok": True, "expression": expression, "result": result}


def eval_math_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
        left = eval_math_node(node.left)
        right = eval_math_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("指数过大")
        return ALLOWED_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPERATORS:
        return ALLOWED_OPERATORS[type(node.op)](eval_math_node(node.operand))
    raise ValueError("只允许数字和基础数学运算符")


def get_current_time(timezone="Asia/Shanghai"):
    timezone = timezone or "Asia/Shanghai"
    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"无效时区：{timezone}") from exc
    now = datetime.now(tz)
    return {
        "ok": True,
        "timezone": timezone,
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "iso_time": now.isoformat(timespec="seconds"),
    }


def search_docs(query, top_k=5):
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query 不能为空")
    top_k = normalize_top_k(top_k)

    ensure_stage4_import_path()
    from rag_pipeline import RAGPipeline

    pipeline = RAGPipeline()
    results = pipeline.search(query, top_k)
    return {
        "ok": True,
        "query": query,
        "results": [
            {
                "source": item["source"],
                "lines": f"{item['start_line']}-{item['end_line']}",
                "score": item["score"],
                "heading_path": item.get("heading_path", ""),
                "text": item["text"][:1200],
            }
            for item in results
        ],
    }


def read_file(path):
    safe_path = resolve_safe_read_path(path)
    content = safe_path.read_text(encoding="utf-8", errors="ignore")
    return {
        "ok": True,
        "path": str(safe_path.relative_to(PROJECT_ROOT)),
        "content": content,
    }


def write_note(title, content):
    validate_note_content(content)
    note_path = build_safe_note_path(title)
    if note_path.exists():
        raise FileExistsError(f"笔记已存在：{note_path.name}")
    note_path.write_text(f"# {title.strip()}\n\n{content.strip()}\n", encoding="utf-8")
    return {
        "ok": True,
        "path": str(note_path.relative_to(PROJECT_ROOT)),
    }


def normalize_top_k(top_k):
    try:
        value = int(top_k)
    except (TypeError, ValueError):
        value = 5
    return max(1, min(value, 10))


def ensure_stage4_import_path():
    stage4_path = str(STAGE4_DIR)
    if stage4_path not in sys.path:
        sys.path.insert(0, stage4_path)
