import numpy as np
from sentence_transformers import SentenceTransformer

from rag_config import EMBEDDING_MODEL_NAME


class EmbeddingModel:
    def __init__(self, model_name=EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts):
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 32,
        )
        return embeddings.astype(np.float32)
