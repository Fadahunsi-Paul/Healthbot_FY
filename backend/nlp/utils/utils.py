# nlp/utils.py
import re
import pandas as pd
from difflib import get_close_matches

# Normalize text
def normalize_query(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

# Simple synonym replacements (expandable)
def canonicalize_condition_terms(query: str) -> str:
    replacements = {
        "bp": "blood pressure",
        "sugar": "diabetes",
        "tb": "tuberculosis",
    }
    q = normalize_query(query)
    for k, v in replacements.items():
        q = q.replace(k, v)
    return q

def normalize_intent_phrases(query: str) -> str:
    q = query.lower()
    patterns = {
        r"(how do i treat|how to cure|cure for)": "treatment for",
        r"(signs of|symptoms of|how do i know if i have)": "symptoms of",
        r"(how to prevent|ways to avoid)": "prevention of",
    }
    for pat, rep in patterns.items():
        q = re.sub(pat, rep, q)
    return q

# Add history context
def improve_query_with_context(query: str, history=None) -> str:
    if not history:
        return query
    last_user = next((m["message"] for m in reversed(history) if m["sender"] == "user"), None)
    if last_user and "it" in query.lower():
        return f"{last_user} {query}"
    return query

# Rewrite follow-up queries
def rewrite_followup_query(query: str, history=None) -> str:
    if not history:
        return query
    if query.lower().startswith(("and ", "what about", "how about")):
        last_user = next((m["message"] for m in reversed(history) if m["sender"] == "user"), None)
        if last_user:
            return f"{last_user} {query}"
    return query

# ---- Dataset lookup ----
DATASET_PATH = "api/dataset/train.csv"
_df_cache = None

def load_dataset():
    global _df_cache
    if _df_cache is None:
        df = pd.read_csv(DATASET_PATH).fillna("")
        df["__norm_cached__"] = df["Question"].apply(normalize_query)
        _df_cache = df
    return _df_cache

def smart_dataset_lookup(query: str, label: str | None = None) -> str | None:
    df = load_dataset()
    q_norm = normalize_query(query)

    # Exact match
    exact = df[df["__norm_cached__"] == q_norm]
    if not exact.empty:
        if label:
            exact_label = exact[exact["qtype"] == label]
            if not exact_label.empty:
                return exact_label.iloc[0]["Answer"]
        return exact.iloc[0]["Answer"]

    # Fuzzy match
    close_norm = get_close_matches(q_norm, df["__norm_cached__"].tolist(), n=1, cutoff=0.8)
    if close_norm:
        candidate_norm = close_norm[0]
        candidate_row = df[df["__norm_cached__"] == candidate_norm]
        if not candidate_row.empty:
            if label:
                exact_label = candidate_row[candidate_row["qtype"] == label]
                if not exact_label.empty:
                    return exact_label.iloc[0]["Answer"]
            return candidate_row.iloc[0]["Answer"]

    return None
