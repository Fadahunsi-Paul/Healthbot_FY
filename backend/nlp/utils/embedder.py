# __define-ocg__ embedding + retrieval logic
import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "train_augmented.csv")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings.npy")

# Load SBERT model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Global storage
questions, answers, embeddings = None, None, None

def load_embeddings():
    """Load dataset + embeddings from disk"""
    global questions, answers, embeddings
    df = pd.read_csv(DATASET_PATH)
    questions = df["question"].astype(str).tolist()
    answers = df["answer"].astype(str).tolist()

    if os.path.exists(EMBEDDINGS_PATH):
        embeddings = np.load(EMBEDDINGS_PATH)
    else:
        embeddings = model.encode(questions, convert_to_numpy=True, show_progress_bar=True)
        np.save(EMBEDDINGS_PATH, embeddings)

def embed_text(texts):
    """Embed text using the sentence transformer model"""
    if isinstance(texts, str):
        texts = [texts]
    return model.encode(texts, convert_to_numpy=True)

def get_answer(query: str, threshold: float = 0.65) -> str:
    """Retrieve best answer or say I don't know if similarity < threshold"""
    global embeddings, questions, answers
    if embeddings is None:
        load_embeddings()

    query_embedding = model.encode(query, convert_to_numpy=True)
    similarities = util.cos_sim(query_embedding, embeddings)[0].cpu().numpy()
    best_idx = int(np.argmax(similarities))
    best_score = similarities[best_idx]

    if best_score < threshold:
        return "Sorry, I don't know the answer to that yet."

    return answers[best_idx]
