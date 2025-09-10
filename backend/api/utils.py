import joblib
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
svm = joblib.load(os.path.join(current_dir, "svm_model.pkl"))
vectorizer = joblib.load(os.path.join(current_dir, "tfidf_vectorizer.pkl"))

def classify_question(question: str) -> str:
    vec = vectorizer.transform([question])
    prediction = svm.predict(vec)[0]
    return prediction
