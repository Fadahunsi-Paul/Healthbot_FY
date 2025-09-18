# nlp/utils/retriever.py
import os
import json
import faiss
import numpy as np
from django.conf import settings
from .embedder import embed_text

FAISS_INDEX_PATH = os.path.join(settings.BASE_DIR, "api", "dataset", "faiss_index.idx")
FAISS_META_PATH = os.path.join(settings.BASE_DIR, "api", "dataset", "faiss_index_meta.json")

class FaissRetriever:
    def __init__(self):
        if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(FAISS_META_PATH):
            raise RuntimeError("FAISS index or metadata not found. Run `python manage.py build_embeddings` first.")
        self.index = faiss.read_index(FAISS_INDEX_PATH)
        with open(FAISS_META_PATH, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

    def search(self, query: str, top_k: int = 3):
        emb = embed_text([query]).astype("float32")
        D, I = self.index.search(emb, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self.meta):
                continue
            item = self.meta[idx]
            results.append({
                "question": item["question"],
                "answer": item["answer"],
                "qtype": item.get("qtype", ""),
                "score": float(score)
            })
        return results
