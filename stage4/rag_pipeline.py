import os
import re

from openai import OpenAI

from document_loader import load_documents
from embedding_model import EmbeddingModel
from rag_config import (
    ARK_BASE_URL,
    CHAT_MODEL,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    MIN_SCORE,
    TOP_K,
    USE_KEYWORD_RERANK,
)
from text_splitter import split_documents
from vector_store import VectorStore


ANSWER_SYSTEM_PROMPT = """
你是一个严谨的本地知识库问答助手。

要求：
1. 只能基于提供的资料回答。
2. 如果资料中没有足够信息，请回答“不知道”。
3. 不要编造资料中不存在的事实。
4. 回答中涉及资料内容时，请使用 [来源编号] 标注依据。
5. 最后列出使用到的来源。
""".strip()


class RAGPipeline:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()
        self.client = build_client()

    def ingest(self, path):
        documents = load_documents(path)
        chunks = split_documents(documents, CHUNK_SIZE, CHUNK_OVERLAP)
        if not chunks:
            return {"documents": len(documents), "chunks": 0}

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts)
        self.vector_store.add(embeddings, chunks)
        return {"documents": len(documents), "chunks": len(chunks)}

    def search(self, question, top_k=TOP_K):
        query_embedding = self.embedding_model.encode([question])[0]
        results = self.vector_store.search(query_embedding, top_k)
        if USE_KEYWORD_RERANK:
            results = keyword_rerank(question, results)
        return results

    def answer(self, question, top_k=TOP_K):
        results = self.search(question, top_k)
        confident_results = [item for item in results if item["score"] >= MIN_SCORE]
        if not confident_results:
            return "不知道。知识库中没有检索到足够相关的资料。", results

        messages = build_answer_messages(question, confident_results)
        response = self.client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=0,
        )
        answer_text = response.choices[0].message.content.strip()
        answer_text = remove_invalid_citations(answer_text, len(confident_results))
        return answer_text, confident_results


def build_client():
    api_key = os.getenv("APIKey")
    if not api_key:
        raise RuntimeError("请先设置环境变量 APIKey")
    return OpenAI(api_key=api_key, base_url=ARK_BASE_URL)


def keyword_rerank(question, results):
    keywords = extract_keywords(question)
    reranked = []
    for item in results:
        hit_count = sum(1 for keyword in keywords if keyword in item["text"])
        item = dict(item)
        item["keyword_hits"] = hit_count
        item["rerank_score"] = item["score"] + 0.05 * hit_count
        reranked.append(item)
    return sorted(reranked, key=lambda item: item["rerank_score"], reverse=True)


def extract_keywords(text):
    words = re.findall(r"[\w\u4e00-\u9fff]+", text.lower())
    return [word for word in words if len(word) >= 2]


def build_answer_messages(question, results):
    context = format_context(results)
    user_prompt = f"""
请基于以下资料回答用户问题。

资料：
{context}

用户问题：
{question}
""".strip()
    return [
        {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def format_context(results):
    sections = []
    for index, item in enumerate(results, start=1):
        heading = f" heading={item['heading_path']}" if item.get("heading_path") else ""
        sections.append(
            f"[来源{index}] source={item['source']} lines={item['start_line']}-{item['end_line']}{heading}\n"
            f"{item['text']}"
        )
    return "\n\n".join(sections)


def remove_invalid_citations(answer, max_source_number):
    def replace(match):
        number = int(match.group(1))
        if 1 <= number <= max_source_number:
            return match.group(0)
        return ""

    return re.sub(r"\[来源(\d+)\]", replace, answer)
