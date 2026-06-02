import json

import faiss
import numpy as np

from rag_config import FAISS_INDEX_PATH, INDEX_DIR, METADATA_PATH


class VectorStore:
    def __init__(self, index_path=FAISS_INDEX_PATH, metadata_path=METADATA_PATH):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = []
        self.load()

    def load(self):
        if self.index_path.exists() and self.metadata_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        else:
            self.index = None
            self.metadata = []

    def save(self):
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
        self.metadata_path.write_text(
            json.dumps(self.metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def clear(self):
        self.index = None
        self.metadata = []
        if self.index_path.exists():
            self.index_path.unlink()
        if self.metadata_path.exists():
            self.metadata_path.unlink()

    def add(self, embeddings, chunks):
        if len(embeddings) != len(chunks):
            raise ValueError("embeddings and chunks length mismatch")
        if len(chunks) == 0:
            return

        embeddings = np.asarray(embeddings, dtype=np.float32)
        dimension = embeddings.shape[1]
        if self.index is None:
            self.index = faiss.IndexFlatIP(dimension)
        elif self.index.d != dimension:
            raise ValueError(
                f"Embedding dimension mismatch: index={self.index.d}, embeddings={dimension}"
            )

        start_id = len(self.metadata)
        normalized_chunks = []
        for offset, chunk in enumerate(chunks):
            item = dict(chunk)
            item["global_chunk_id"] = start_id + offset
            normalized_chunks.append(item)

        self.index.add(embeddings)
        self.metadata.extend(normalized_chunks)
        self.save()

    def search(self, query_embedding, top_k):
        if self.index is None or self.index.ntotal == 0:
            return []

        query_embedding = np.asarray(query_embedding, dtype=np.float32)
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        results = []
        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue
            item = dict(self.metadata[index])
            item["score"] = float(score)
            results.append(item)
        return results

    def stats(self):
        return {
            "chunks": len(self.metadata),
            "vectors": 0 if self.index is None else self.index.ntotal,
            "index_path": str(self.index_path),
            "metadata_path": str(self.metadata_path),
        }
