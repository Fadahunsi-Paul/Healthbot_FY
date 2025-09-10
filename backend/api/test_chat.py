# test_chat.py
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------------------
# Load model + vectorizer
# ------------------------------
svm = joblib.load("svm_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

# Load dataset for retrieval
df = pd.read_csv("dataset/train.csv")

# Group into dictionary by label (qtype)
qa_dict = df.groupby("qtype")[["Question", "Answer"]].apply(
    lambda x: x.to_dict("records")
).to_dict()

# ------------------------------
# Helper functions
# ------------------------------
def classify_question(question: str) -> str:
    """Classify user question into label using trained SVM."""
    vec = vectorizer.transform([question])
    return svm.predict(vec)[0]

def get_answer(question: str, label: str) -> str:
    """Retrieve best matching answer, enforcing disease filter if possible."""
    if label not in qa_dict:
        return "Sorry, I don't have an answer for that yet."

    candidates = qa_dict[label]
    candidate_questions = [c["Question"] for c in candidates]
    candidate_answers = [c["Answer"] for c in candidates]

    # Step 1: detect possible disease keyword from the query
    DISEASES = ["malaria", "diabetes", "cancer", "kidney", "asthma", "hiv"]
    disease = next((d for d in DISEASES if d in question.lower()), None)

    # Step 2: disease filtering - prefer candidates that mention the disease
    if disease:
        filtered_candidates = [
            (q, a) for q, a in zip(candidate_questions, candidate_answers)
            if disease in q.lower() or disease in a.lower()
        ]
        # If we found disease-specific candidates, use them
        if filtered_candidates:
            candidate_questions, candidate_answers = zip(*filtered_candidates)
        # If no disease-specific candidates found, fall back to all candidates

    # Step 3: TF-IDF retrieval using the pre-trained vectorizer
    try:
        tfidf_matrix = vectorizer.transform(candidate_questions)
        query_vec = vectorizer.transform([question])
        scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    except Exception as e:
        # Fallback: if vectorizer fails, return first candidate
        return candidate_answers[0] if candidate_answers else "Sorry, I don't have an answer for that yet."

    if len(scores) == 0 or scores.max() == 0:
        return f"Sorry, I don't have a specific answer about {disease or 'this topic'} for {label}."

    best_idx = scores.argmax()
    return candidate_answers[best_idx]

def chatbot_response(question: str) -> dict:
    """Full pipeline: classify -> retrieve -> return response."""
    label = classify_question(question)
    answer = get_answer(question, label)
    return {
        "question": question,
        "predicted_label": label,
        "answer": answer
    }

# ------------------------------
# Quick test run
# ------------------------------
if __name__ == "__main__":
    test_questions = [
        "What are the causes of malaria?",
        "How can I prevent diabetes?",
        "What are the symptoms of malaria?",
        "Tell me about treatment options for diabetes",
        "Where can I find support groups?"
    ]

    for q in test_questions:
        response = chatbot_response(q)
        print("\n❓ Question:", response["question"])
        print("🔖 Predicted Label:", response["predicted_label"])
        print("💡 Answer:", response["answer"][:300], "...")
