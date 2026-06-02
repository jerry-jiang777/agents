from rag_config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL_NAME,
    MIN_SCORE,
    TOP_K,
    USE_KEYWORD_RERANK,
)
from rag_pipeline import RAGPipeline


def print_help():
    print(
        """
可用命令：
/help                 查看帮助
/ingest <path>        导入单个文件或目录
/search <question>    只检索相关片段，不调用 LLM
/ask <question>       基于知识库问答，答案带引用
/stats                查看当前索引状态
/config               查看当前 RAG 参数
/clear_index          清空向量索引和 metadata
quit / exit / 退出     退出程序
""".strip()
    )


def print_config():
    print(
        f"""
当前配置：
EMBEDDING_MODEL_NAME = {EMBEDDING_MODEL_NAME}
CHUNK_SIZE = {CHUNK_SIZE}
CHUNK_OVERLAP = {CHUNK_OVERLAP}
TOP_K = {TOP_K}
MIN_SCORE = {MIN_SCORE}
USE_KEYWORD_RERANK = {USE_KEYWORD_RERANK}
""".strip()
    )


def print_search_results(results):
    if not results:
        print("没有检索到结果。")
        return

    for index, item in enumerate(results, start=1):
        rerank_text = ""
        if "rerank_score" in item:
            rerank_text = f" rerank_score={item['rerank_score']:.4f} keyword_hits={item['keyword_hits']}"
        heading = f" heading={item['heading_path']}" if item.get("heading_path") else ""
        print(
            f"\n[{index}] score={item['score']:.4f}{rerank_text}\n"
            f"source={item['source']} lines={item['start_line']}-{item['end_line']}{heading}\n"
            f"{item['text'][:600]}"
        )


def main():
    print("正在加载 RAG 系统，首次加载 embedding 模型可能较慢...")
    pipeline = RAGPipeline()
    print("RAG 知识库问答系统已启动。输入 /help 查看命令。")

    while True:
        user_input = input("\nRAG> ").strip()
        if not user_input:
            continue

        command = user_input.lower()
        if command in ["quit", "exit", "退出"]:
            print("已退出。")
            break
        if command == "/help":
            print_help()
            continue
        if command == "/config":
            print_config()
            continue
        if command == "/stats":
            stats = pipeline.vector_store.stats()
            print(
                f"chunks={stats['chunks']} vectors={stats['vectors']}\n"
                f"index_path={stats['index_path']}\n"
                f"metadata_path={stats['metadata_path']}"
            )
            continue
        if command == "/clear_index":
            pipeline.vector_store.clear()
            print("索引已清空。")
            continue
        if command.startswith("/ingest "):
            path = user_input.split(maxsplit=1)[1]
            try:
                stats = pipeline.ingest(path)
            except Exception as exc:
                print(f"导入失败：{exc}")
                continue
            print(f"导入完成：documents={stats['documents']} chunks={stats['chunks']}")
            continue
        if command.startswith("/search "):
            question = user_input.split(maxsplit=1)[1]
            results = pipeline.search(question, TOP_K)
            print_search_results(results)
            continue
        if command.startswith("/ask "):
            question = user_input.split(maxsplit=1)[1]
            try:
                answer, results = pipeline.answer(question, TOP_K)
            except Exception as exc:
                print(f"问答失败：{exc}")
                continue
            print(f"\n答案：\n{answer}")
            print("\n---检索来源---")
            print_search_results(results)
            continue

        print("未知命令。输入 /help 查看帮助。")


if __name__ == "__main__":
    main()
