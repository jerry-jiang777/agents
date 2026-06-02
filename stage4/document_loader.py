from pathlib import Path

from rag_config import SUPPORTED_EXTENSIONS


def load_documents(path):
    """加载单个文件或目录中的支持类型文档。"""
    input_path = Path(path).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Path not found: {input_path}")

    files = [input_path] if input_path.is_file() else collect_files(input_path)
    documents = []
    for file_path in files:
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        text = read_text_file(file_path)
        if not text.strip():
            continue
        documents.append(
            {
                "source": str(file_path),
                "text": text,
                "lines": text.splitlines(),
            }
        )
    return documents


def collect_files(directory):
    ignored_dirs = {".git", "__pycache__", ".venv", "venv", "indexes"}
    files = []
    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue
        if any(part in ignored_dirs for part in file_path.parts):
            continue
        if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(file_path)
    return sorted(files)


def read_text_file(file_path):
    encodings = ["utf-8", "utf-8-sig", "gbk"]
    for encoding in encodings:
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return file_path.read_text(encoding="utf-8", errors="ignore")
