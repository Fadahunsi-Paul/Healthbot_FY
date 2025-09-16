# nlp/services/unified_service.py
import re
import os
import pandas as pd
from django.conf import settings
from api.qa_lookup import get_answer as qa_lookup_answer
from nlp.utils import find_best_answers
from nlp.cache_utils import get_cached_answer, set_cached_answer
from api.utils.smalltalk import check_smalltalk

DATA_CSV = os.path.join(settings.BASE_DIR, "api", "dataset", "train.csv")
FAISS_SCORE_THRESHOLD = 0.5  # Lower threshold for better matching
FUZZY_CUTOFF = 0.9

# Disease aliases
DISEASE_ALIASES = {
    "malaria": ["malaria", "plasmodium", "mosquito fever"],
    "diabetes": ["diabetes", "blood sugar", "hyperglycemia"],
    "fever": ["fever", "temperature", "pyrexia"],
}

# Intent keywords
INTENT_KEYWORDS = {
    "cause": ["cause", "causes", "reason", "etiology", "why", "how do you get", "what causes"],
    "symptom": ["symptom", "symptoms", "signs", "manifestation", "feel like", "what does it feel"],
    "treatment": ["treatment", "treat", "cure", "manage", "therapy", "medication", "medicine"],
    "prevention": ["prevent", "prevention", "avoid", "reduce risk", "vaccine", "protect"],
}

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

def get_disease_from_query(query: str) -> str:
    """Extract disease name from query using aliases"""
    query_lower = query.lower()
    for disease, aliases in DISEASE_ALIASES.items():
        if any(alias in query_lower for alias in aliases):
            return disease
    return None

def improve_query_with_context(query: str, context: str = None, history: list = None) -> str:
    """Improve context-dependent queries by extracting context from history"""
    query_lower = query.lower().strip()
    
    # Handle vague queries that need context
    vague_patterns = [
        r'^(how to (cure|treat|fix|heal) it\??)$',
        r'^(cure it\??)$',
        r'^(treat it\??)$',
        r'^(what (is|are) the (symptoms?|causes?|treatment)\??)$',
        r'^(how to prevent it\??)$'
    ]
    
    if any(re.match(pattern, query_lower) for pattern in vague_patterns):
        # Try to get disease/condition from recent history
        if history:
            for msg in reversed(history[-5:]):  # Check last 5 messages
                if msg.get("sender") == "user":
                    prev_query = msg.get("message", "").lower()
                    # Look for disease mentions
                    for disease, aliases in DISEASE_ALIASES.items():
                        if any(alias in prev_query for alias in aliases):
                            # Reconstruct query with context
                            if "cure" in query_lower or "treat" in query_lower:
                                return f"how to treat {disease}"
                            elif "prevent" in query_lower:
                                return f"how to prevent {disease}"
                            elif "symptom" in query_lower:
                                return f"what are {disease} symptoms"
                            elif "cause" in query_lower:
                                return f"what causes {disease}"
                            break
    
    return query

def smart_dataset_lookup(user_query: str, label: str = None):
    """Improved dataset lookup with semantic understanding"""
    if not os.path.exists(DATA_CSV):
        return None
    
    df = pd.read_csv(DATA_CSV).fillna("")
    query_lower = user_query.lower()
    
    # Priority 1: Exact phrase matches in our cleaned data
    priority_patterns = {
        "headache": ["headache", "head pain", "migraine"],
        "malaria": ["malaria", "plasmodium", "mosquito fever"],
        "diabetes": ["diabetes", "blood sugar", "hyperglycemia"], 
        "fever": ["fever", "temperature", "pyrexia"]
    }
    
    # Check for priority conditions first
    for condition, patterns in priority_patterns.items():
        if any(pattern in query_lower for pattern in patterns):
            # Look for our cleaned entries for this condition
            condition_mask = df['Question'].str.contains(condition, case=False, na=False)
            condition_df = df[condition_mask]
            
            if not condition_df.empty:
                # If label specified, filter by it
                if label:
                    label_matches = condition_df[condition_df['qtype'] == label]
                    if not label_matches.empty:
                        return label_matches.iloc[0]['Answer']
                
                # Otherwise, find best match by intent
                intent_order = ['symptom', 'cause', 'treatment', 'prevention', 'information']
                
                # Try to match query intent
                if any(word in query_lower for word in ['cause', 'causes', 'why', 'reason']):
                    cause_matches = condition_df[condition_df['qtype'] == 'cause']
                    if not cause_matches.empty:
                        return cause_matches.iloc[0]['Answer']
                
                if any(word in query_lower for word in ['treat', 'cure', 'therapy', 'medicine']):
                    treat_matches = condition_df[condition_df['qtype'] == 'treatment']
                    if not treat_matches.empty:
                        return treat_matches.iloc[0]['Answer']
                
                if any(word in query_lower for word in ['symptom', 'signs', 'feel', 'have']):
                    symptom_matches = condition_df[condition_df['qtype'] == 'symptom']
                    if not symptom_matches.empty:
                        return symptom_matches.iloc[0]['Answer']
                
                # Fallback to first available entry for this condition
                return condition_df.iloc[0]['Answer']
    
    # Priority 2: General symptom matching
    symptom_indicators = ['i have', 'i feel', 'experiencing', 'suffering from']
    if any(indicator in query_lower for indicator in symptom_indicators):
        symptom_df = df[df['qtype'] == 'symptom']
        if not symptom_df.empty:
            # Look for keyword matches in symptom entries
            for _, row in symptom_df.iterrows():
                question_lower = row['Question'].lower()
                # Extract key words from user query (exclude common words)
                query_words = [w for w in query_lower.split() if w not in ['i', 'have', 'am', 'feel', 'the', 'a', 'an']]
                if any(word in question_lower for word in query_words):
                    return row['Answer']
    
    # Priority 3: Fuzzy matching as before
    import difflib
    if label:
        df = df[df["qtype"] == label]
    if df.empty:
        return None
    
    questions = df["Question"].astype(str).tolist()
    norm_questions = [q.strip().lower() for q in questions]
    close = difflib.get_close_matches(query_lower, norm_questions, n=1, cutoff=0.6)  # Lower cutoff
    if close:
        idx = norm_questions.index(close[0])
        return df["Answer"].iloc[idx]
    
    return None

def re_rank_by_intent(query: str, candidates: list[dict]) -> str | None:
    query_lc = query.lower()
    for intent, kws in INTENT_KEYWORDS.items():
        if any(kw in query_lc for kw in kws):
            for cand in candidates:
                if any(kw in cand["question"].lower() for kw in kws):
                    return cand["answer"]
    return None

def get_disease_from_query(query: str) -> str | None:
    query_lc = query.lower()
    for disease, aliases in DISEASE_ALIASES.items():
        if any(alias in query_lc for alias in aliases):
            return disease
    return None

# Unified answer function
def get_answer(user_question: str, label: str = None, context: str = None, history: list = None) -> str:
    # Improve context-dependent queries
    user_question = improve_query_with_context(user_question, context, history)
    norm_query = normalize_text(user_question)

    # 0️⃣ Smalltalk check
    smalltalk_resp = check_smalltalk(user_question)
    if smalltalk_resp:
        return smalltalk_resp

    # 1️⃣ Cache check
    cached = get_cached_answer(norm_query)
    if cached:
        return cached

    # 2️⃣ Disease + intent direct lookup
    disease = get_disease_from_query(user_question)
    intent = None
    for key, kws in INTENT_KEYWORDS.items():
        if any(kw in norm_query for kw in kws):
            intent = key
            break

    if disease and intent:
        # Fuzzy dataset lookup first
        ans = dataset_fuzzy_lookup(norm_query, label=intent)
        if ans:
            set_cached_answer(norm_query, ans)
            return ans

        # Hardcoded fallback answers
        HARDCODED_ANSWERS = {
            "malaria": {
                "cause": "Malaria is caused by Plasmodium parasites that are transmitted to humans through the bites of infected female Anopheles mosquitoes. There are five parasite species that cause malaria in humans: P. falciparum (most deadly), P. vivax, P. ovale, P. malariae, and P. knowlesi.",
                "symptom": "Malaria symptoms typically appear 10-15 days after infection and include fever and chills, headache, nausea and vomiting, muscle pain and fatigue, abdominal pain, diarrhea, anemia, and jaundice (yellowing of skin and eyes).",
                "treatment": "Malaria treatment depends on the parasite species and severity. Common treatments include Artemisinin-based combination therapies (ACTs) for P. falciparum malaria, Chloroquine for P. vivax/ovale/malariae in sensitive areas, and IV artesunate for severe malaria.",
                "prevention": "Malaria prevention includes using insecticide-treated bed nets, indoor residual spraying, taking antimalarial medications when traveling to endemic areas, wearing protective clothing, and using insect repellent with DEET."
            }
        }
        answer = HARDCODED_ANSWERS.get(disease, {}).get(intent)
        if answer:
            set_cached_answer(norm_query, answer)
            return answer

    # 3️⃣ SVM + TF-IDF pipeline
    ans = qa_lookup_answer(user_question, label, context=context, history=history)
    if ans:
        set_cached_answer(norm_query, ans)
        return ans

    # 4️⃣ FAISS semantic search
    try:
        results = find_best_answers(user_question, top_k=5)
        if results:
            candidates = [{"score": s, "answer": m["answer"], "question": m.get("question", ""), "label": m.get("qtype")} for s, m in results]
            if label:
                candidates = [c for c in candidates if c.get("label") == label]
            if candidates:
                best = candidates[0]
                if best["score"] >= FAISS_SCORE_THRESHOLD:
                    intent_ans = re_rank_by_intent(user_question, candidates)
                    if intent_ans:
                        set_cached_answer(norm_query, intent_ans)
                        return intent_ans
                    set_cached_answer(norm_query, best["answer"])
                    return best["answer"]
    except Exception:
        pass

    # 5️⃣ Smart dataset lookup (prioritizes our cleaned data)
    smart_ans = smart_dataset_lookup(user_question, label=label)
    if smart_ans:
        set_cached_answer(norm_query, smart_ans)
        return smart_ans

    # 6️⃣ Default fallback
    default = "Sorry, I don’t have a specific answer for that right now."
    set_cached_answer(norm_query, default)
    return default
