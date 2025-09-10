
import re
import pandas as pd
import joblib
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

df = pd.read_csv("api/dataset/train.csv")
qa_dict = df.groupby("qtype")[["Question", "Answer"]].apply(lambda x: x.to_dict("records")).to_dict()
classifier = joblib.load("api/svm_model.pkl")          # SVM classifier for qtype
tfidf_vectorizer = joblib.load("api/tfidf_vectorizer.pkl")  # Fitted TF-IDF for embeddings

def get_answer(question: str, label: str, context: str = None, history: list = None) -> str:
    query_text = (context + "\nUser: " + question) if context else question

    if label not in qa_dict:
        return "Sorry, I don’t have an answer for that yet."

    candidates = qa_dict[label]
    candidate_questions = [c["Question"] for c in candidates]
    candidate_answers = [c["Answer"] for c in candidates]

    print(f"\n[DEBUG] Query text (used for vector search): {query_text[:200]!r}")
    print(f"[DEBUG] Label: {label}, candidate pool: {len(candidate_questions)}")

    tfidf_matrix = tfidf_vectorizer.transform(candidate_questions)
    query_vec = tfidf_vectorizer.transform([query_text])
    scores = cosine_similarity(query_vec, tfidf_matrix).flatten()

    if scores.max() > 0:
        best_idx = scores.argmax()
        return candidate_answers[best_idx]

    label_df = df[df["qtype"] == label]
    if not label_df.empty:
        q_texts = label_df["Question"].tolist()
        a_texts = label_df["Answer"].tolist()
        tfidf_matrix2 = tfidf_vectorizer.transform(q_texts)
        scores2 = cosine_similarity(query_vec, tfidf_matrix2).flatten()
        if scores2.max() > 0:
            return a_texts[scores2.argmax()]

    if history:
        last_user = None
        for msg in reversed(history):
            if msg.get("sender") == "user":
                last_user = msg.get("message")
                break
        if last_user:
            tokens = re.findall(r"\b[a-zA-Z]{4,}\b", last_user.lower())
            if tokens:
                # look for rows mentioning any token
                pattern = "|".join(re.escape(t) for t in set(tokens[:6]))  # limit tokens
                mask = df["Question"].str.contains(pattern, case=False, na=False) | df["Answer"].str.contains(pattern, case=False, na=False)
                cand = df[mask]
                if not cand.empty:
                    q_texts = cand["Question"].tolist()
                    a_texts = cand["Answer"].tolist()
                    tfidf_matrix3 = tfidf_vectorizer.transform(q_texts)
                    scores3 = cosine_similarity(query_vec, tfidf_matrix3).flatten()
                    if scores3.max() > 0:
                        return a_texts[scores3.argmax()]

    return "Sorry, I don’t have a specific answer for that right now."