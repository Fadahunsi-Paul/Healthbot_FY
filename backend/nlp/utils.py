# nlp/utils.py
import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from django.conf import settings

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
FAISS_INDEX_PATH = os.path.join(settings.BASE_DIR, "api", "dataset", "faiss_index.idx")
FAISS_META_PATH = os.path.join(settings.BASE_DIR, "api", "dataset", "faiss_index_meta.json")

_model = SentenceTransformer(MODEL_NAME)

if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(FAISS_META_PATH):
    raise RuntimeError("FAISS index or metadata not found. Run build_embeddings first.")

_index = faiss.read_index(FAISS_INDEX_PATH)
with open(FAISS_META_PATH, "r", encoding="utf-8") as f:
    _META = json.load(f)  # list of dicts with keys: question, answer, qtype

def _encode_and_normalize(texts):
    emb = _model.encode(texts, convert_to_numpy=True)
    emb = emb.astype("float32")
    faiss.normalize_L2(emb)
    return emb

def find_best_answers(query, top_k=5, label: str = None):
    """
    Returns list of (score, meta_dict) sorted by score desc.
    If label is provided, returns results where meta['qtype'] == label first (if any),
    otherwise returns the best matches overall.
    """
    q_emb = _encode_and_normalize([query])
    distances, indices = _index.search(q_emb, top_k)
    scores = distances[0].tolist()
    ids = indices[0].tolist()

    results = []
    for idx, score in zip(ids, scores):
        if idx < 0 or idx >= len(_META):
            continue
        meta = _META[idx]
        results.append((float(score), meta))

    if label:
        # Prefer same-label results: partition
        same_label = [r for r in results if r[1].get("qtype", "").lower() == (label or "").lower()]
        other = [r for r in results if r[1].get("qtype", "").lower() != (label or "").lower()]
        # If we found some same_label results, return them first (still sorted by score)
        if same_label:
            return same_label + other
    return results
