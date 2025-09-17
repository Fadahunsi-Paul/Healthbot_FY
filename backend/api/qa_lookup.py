# nlp/services/qa_lookup.py
import re
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Load data & models
df = pd.read_csv("api/dataset/train.csv")
qa_dict = (
    df.groupby("qtype")[["Question", "Answer"]]
    .apply(lambda x: x.to_dict("records"))
    .to_dict()
)
classifier = joblib.load("api/svm_model.pkl")
tfidf_vectorizer: TfidfVectorizer = joblib.load("api/tfidf_vectorizer.pkl")

# Config
# Balance precision and recall for paraphrases while avoiding hallucinations
TFIDF_THRESHOLD = 0.62
TOP_K = 5              # number of candidates to re-rank

def rerank_candidates(query: str, candidates: list[dict], query_vec):
    """Re-rank TF-IDF candidates using keyword overlap."""
    candidate_questions = [c["Question"] for c in candidates]
    candidate_answers = [c["Answer"] for c in candidates]

    tfidf_matrix = tfidf_vectorizer.transform(candidate_questions)
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    # Take top K matches
    top_idx = scores.argsort()[-TOP_K:][::-1]
    top_candidates = [(scores[i], candidate_answers[i], candidate_questions[i]) for i in top_idx]

    # Add keyword overlap boost
    query_tokens = set(re.findall(r"\b[a-zA-Z]{4,}\b", query.lower()))
    best_score, best_answer = 0, None
    for s, ans, q in top_candidates:
        q_tokens = set(re.findall(r"\b[a-zA-Z]{4,}\b", q.lower()))
        overlap = len(query_tokens & q_tokens)
        final_score = s + (0.05 * overlap)  # small boost for keyword overlap
        if final_score > best_score:
            best_score, best_answer = final_score, ans

    return best_answer if best_score >= TFIDF_THRESHOLD else None

def get_answer(query: str, label: str = None, context: str = None, history: list = None) -> str | None:
    """
    Lookup an answer for the given query using SVM/TF-IDF similarity.
    Returns None if no confident match is found.
    """
    query_text = (context + "\nUser: " + query) if context else query
    query_vec = tfidf_vectorizer.transform([query_text])

    if label and label in qa_dict:
        # Primary: search within predicted label
        candidates = qa_dict[label]
        best = rerank_candidates(query, candidates, query_vec)
        if best:
            return best

        # Secondary: allow nearby candidates within the same label dataframe (duplicates removed)
        label_df = df[df["qtype"] == label]
        if not label_df.empty:
            fallback_candidates = label_df[["Question", "Answer"]].drop_duplicates().to_dict("records")
            best = rerank_candidates(query, fallback_candidates, query_vec)
            if best:
                return best

    # Cross-label fallback: search across the entire dataset if label-specific search failed
    all_candidates = df[["Question", "Answer"]].drop_duplicates().to_dict("records")
    best = rerank_candidates(query, all_candidates, query_vec)
    if best:
        return best

    # Last resort: history-based keyword match
    if history:
        last_user = None
        for msg in reversed(history):
            if msg.get("sender") == "user":
                last_user = msg.get("message")
                break
        if last_user:
            tokens = re.findall(r"\b[a-zA-Z]{4,}\b", last_user.lower())
            if tokens:
                pattern = "|".join(re.escape(t) for t in set(tokens[:6]))
                mask = df["Question"].str.contains(pattern, case=False, na=False) | df["Answer"].str.contains(pattern, case=False, na=False)
                cand = df[mask]
                if not cand.empty:
                    hist_candidates = cand[["Question", "Answer"]].to_dict("records")
                    best = rerank_candidates(query, hist_candidates, query_vec)
                    if best:
                        return best

    return None
