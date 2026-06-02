from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INDEX_DIR = BASE_DIR / "indexes"
FAISS_INDEX_PATH = INDEX_DIR / "rag.index"
METADATA_PATH = INDEX_DIR / "metadata.json"

SUPPORTED_EXTENSIONS = {".md", ".txt", ".py"}

CHAT_MODEL = "ep-20260525103710-jgg4p"
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

EMBEDDING_MODEL_NAME = "BAAI/bge-small-zh-v1.5"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 5
MIN_SCORE = 0.25
USE_KEYWORD_RERANK = True
