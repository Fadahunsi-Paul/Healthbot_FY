# nlp/services/unified_service.py
from nlp.utils.utils import (
    normalize_intent_phrases,
    canonicalize_condition_terms,
    improve_query_with_context,
    rewrite_followup_query,
    smart_dataset_lookup,
)
from nlp.utils.retriever import FaissRetriever
from api.utils.smalltalk import check_smalltalk

retriever = None
FAISS_SCORE_THRESHOLD = 0.6  # configurable

def init_retriever():
    global retriever
    if retriever is None:
        retriever = FaissRetriever()
    return retriever

def get_answer(user_query: str, label: str | None = None, history=None) -> str:
    retriever = init_retriever()

    # 1. Normalize + preprocess
    query = normalize_intent_phrases(canonicalize_condition_terms(user_query))
    query = improve_query_with_context(query, history=history)
    query = rewrite_followup_query(query, history)

    # 2. Direct dataset lookup
    dataset_answer = smart_dataset_lookup(query, label)
    if dataset_answer:
        return dataset_answer

    # 3. FAISS semantic retrieval
    results = retriever.search(query, top_k=3)
    if results and results[0]["score"] >= FAISS_SCORE_THRESHOLD:
        return results[0]["answer"]

    # 4. Fallback smalltalk/default
    return check_smalltalk(query) or "Sorry, I don’t know the answer to that."
