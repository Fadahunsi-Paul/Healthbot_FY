# nlp/services/unified_service.py
import re
import os
import pandas as pd
from django.conf import settings
from api.qa_lookup import get_answer as qa_lookup_answer
# Optional dependency: FAISS + sentence-transformers
try:
    from nlp.utils import find_best_answers as _find_best_answers_impl
except Exception:
    _find_best_answers_impl = None
from nlp.cache_utils import get_cached_answer, set_cached_answer
from api.utils.smalltalk import check_smalltalk

DATA_CSV = os.path.join(settings.BASE_DIR, "api", "dataset", "train.csv")
# Stricter thresholds to minimize hallucinations
FAISS_SCORE_THRESHOLD = 0.72
FUZZY_CUTOFF = 0.9
STRICT_MODE = False  # Allow keyword-based lookups for single terms like "malaria", "diabetes"

# Disease aliases
DISEASE_ALIASES = {
    "malaria": ["malaria", "plasmodium", "mosquito fever"],
    "diabetes": ["diabetes", "blood sugar", "hyperglycemia"],
    "fever": ["fever", "temperature", "pyrexia"],
    "hypertension": ["hypertension", "high blood pressure", "htn"],
    "headache": ["headache", "migraine", "head pain"],
    "kidney disease": ["kidney disease", "chronic kidney disease", "ckd", "renal disease"],
    "cancer": ["cancer", "tumor", "neoplasm", "malignancy"],
}

# Intent keywords (extended to cover all dataset qtypes)
INTENT_KEYWORDS = {
    "cause": ["cause", "causes", "reason", "etiology", "why", "how do you get", "what causes"],
    "symptom": ["symptom", "symptoms", "signs", "manifestation", "feel like", "what does it feel"],
    "treatment": ["treatment", "treat", "cure", "manage", "therapy", "medication", "medicine", "management"],
    "prevention": ["prevent", "prevention", "avoid", "reduce risk", "vaccine", "protect"],
    "exams and tests": ["test", "tests", "diagnose", "diagnosis", "screen", "screening"],
    "considerations": ["what to do", "consider", "next steps", "do about"],
    "complications": ["complication", "complications", "risk of", "leads to"],
    "emergency": ["emergency", "urgent", "immediately", "call"],
    "frequency": ["how often", "frequency", "common", "prevalence"],
    "genetic changes": ["mutation", "genetic", "genes", "variants"],
    "inheritance": ["inherit", "inherited", "hereditary", "runs in families"],
    "lifestyle": ["lifestyle", "diet", "exercise", "habits"],
    "mental health": ["mental", "anxiety", "depression", "stress"],
    "outlook": ["outlook", "prognosis", "survival", "long term"],
    "research": ["research", "latest", "trials", "study"],
    "stages": ["stage", "stages", "phase", "phases"],
    "susceptibility": ["susceptible", "at risk", "risk factors", "who gets"],
    "information": ["what is", "what are", "information", "about"],
}

# Phrase-level paraphrase normalization rules (intent canonicalization)
PHRASE_SYNONYMS: list[tuple[re.Pattern, str]] = [
    # Causes
    (re.compile(r"\bhow\s+do\s+(you|people)\s+get\b", re.I), "what causes"),
    (re.compile(r"\bwhat\s+leads\s+to\b", re.I), "what causes"),
    (re.compile(r"\breasons?\s+for\b", re.I), "what causes"),
    (re.compile(r"\bcause\s+of\b", re.I), "what causes"),
    # Symptoms
    (re.compile(r"\bsigns?\s+of\b", re.I), "symptoms of"),
    (re.compile(r"\bhow\s+does\s+([a-z\-\s]+)\s+feel\b\??", re.I), r"what are the symptoms of \1"),
    # Treatment / management
    (re.compile(r"\bhow\s+to\s+cure\b", re.I), "how to treat"),
    (re.compile(r"\bcure\s+for\b", re.I), "treatment for"),
    (re.compile(r"\bmanage(ment)?\s+of\b", re.I), "treatment for"),
    (re.compile(r"\bmedications?\s+for\b", re.I), "treatment for"),
    # Prevention
    (re.compile(r"\bhow\s+can\s+I\s+avoid\b", re.I), "how to prevent"),
    (re.compile(r"\breduce\s+risk\s+of\b", re.I), "how to prevent"),
    (re.compile(r"\bways?\s+to\s+avoid\b", re.I), "how to prevent"),
    # Exams & Tests
    (re.compile(r"\bhow\s+to\s+diagnose\b", re.I), "tests for"),
    (re.compile(r"\bhow\s+is\s+.*\bdiagnosed\b", re.I), "tests for"),
    # Considerations
    (re.compile(r"\bwhat\s+to\s+do\s+for\b", re.I), "what to do for"),
    (re.compile(r"\bwhat\s+should\s+I\s+do\s+for\b", re.I), "what to do for"),
    # Outlook
    (re.compile(r"\bwhat\s+is\s+the\s+prognosis\s+for\b", re.I), "outlook for"),
]

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _mentions_any(text: str, keywords: list[str]) -> bool:
    text_lc = text.lower()
    return any(kw in text_lc for kw in keywords)


def is_cache_consistent_with_query(query: str, cached_answer: str) -> bool:
    """Lightweight guard to avoid serving stale/wrong cached answers.

    If the cached answer contains explicit disease terms that are NOT present in
    the user query, we consider it inconsistent and ignore the cache.
    """
    if not cached_answer:
        return False
    query_lc = query.lower()
    answer_lc = cached_answer.lower()

    disease_terms = [
        "malaria", "diabetes", "headache", "fever", "arthritis",
        "asthma", "cancer", "kidney", "heart", "lupus",
    ]
    for term in disease_terms:
        if term in answer_lc and term not in query_lc:
            return False
    return True

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

def canonicalize_condition_terms(query: str) -> str:
    """Normalize ambiguous condition mentions to the dataset's canonical forms.

    This is a lightweight, rule-based step to improve retrieval when the
    dataset only contains a specific subtype for a commonly used generic name.
    """
    q = query.lower()
    # If user says just "hypertension" (without subtype), prefer pulmonary hypertension
    if re.search(r"\bhypertension\b", q) and not re.search(r"\b(pulmonary|portal)\b", q):
        query = re.sub(r"\bhypertension\b", "pulmonary hypertension", query, flags=re.IGNORECASE)

    # Dataset-driven aliases (acronyms and aka mappings)
    aliases = _load_aliases_from_dataset()
    lowered = query.lower()
    for alias, canonical in aliases.items():
        if alias in lowered and canonical not in lowered:
            pattern = re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)
            query = pattern.sub(canonical, query)
            lowered = query.lower()
    return query

def normalize_intent_phrases(query: str) -> str:
    """Apply regex-based paraphrase rules to rewrite to canonical phrasing.

    This operates conservatively: it only changes well-known patterns and
    preserves disease terms, which helps TF‑IDF retrieval without hallucinating.
    """
    new_q = query
    for pattern, repl in PHRASE_SYNONYMS:
        try:
            new_q = pattern.sub(repl, new_q)
        except Exception:
            # Avoid any unexpected regex failures; keep original
            pass
    return new_q

def detect_intent_from_text(text: str) -> str | None:
    text_lc = (text or "").lower()
    
    # Enhanced pattern matching for better follow-up detection
    if re.search(r"\b(how\s+is\s+it\s+treated?|how\s+do\s+i\s+treat\s+it|how\s+to\s+treat\s+it)\b", text_lc):
        return "treatment"
    if re.search(r"\b(how\s+is\s+it\s+prevented?|how\s+do\s+i\s+prevent\s+it|how\s+to\s+prevent\s+it)\b", text_lc):
        return "prevention"
    if re.search(r"\b(what\s+are\s+the\s+symptoms?|what\s+about\s+symptoms?|how\s+do\s+i\s+know\s+if\s+i\s+have\s+it)\b", text_lc):
        return "symptom"
    if re.search(r"\b(what\s+causes\s+it|why\s+do\s+i\s+get\s+it|how\s+do\s+i\s+get\s+it)\b", text_lc):
        return "cause"
    
    # Original keyword matching
    for intent, kws in INTENT_KEYWORDS.items():
        if any(kw in text_lc for kw in kws):
            return intent
    
    # Shorthand follow-ups: "what about symptoms/treatment/..."
    if re.search(r"\b(symptoms?|treatment|treat|causes?|prevention|prevent)\b", text_lc):
        if re.search(r"symptom|sign", text_lc):
            return "symptom"
        if re.search(r"treat|treatment|cure|manage", text_lc):
            return "treatment"
        if re.search(r"cause|why|how do you get", text_lc):
            return "cause"
        if re.search(r"prevent|reduce risk|avoid", text_lc):
            return "prevention"
    return None

def _build_condition_index() -> tuple[set[str], dict[str, str]]:
    """Return (conditions_set, alias_map) using dataset extraction and aliases."""
    conditions = extract_entities_from_dataset() | extract_medical_conditions_from_dataset()
    # Add disease aliases as simple expansions
    alias_map: dict[str, str] = {}
    for canonical, aliases in DISEASE_ALIASES.items():
        for alias in aliases:
            alias_map[alias.lower()] = canonical.lower()
        conditions.add(canonical.lower())
    # Add dataset-driven aliases (acronyms, aka)
    try:
        dataset_aliases = _load_aliases_from_dataset()
        for alias, canonical in dataset_aliases.items():
            alias_map[alias.lower()] = canonical.lower()
            conditions.add(canonical.lower())
    except Exception:
        pass
    return conditions, alias_map

def detect_recent_condition(history: list, current_text: str = "") -> str | None:
    """Find the most recent condition mention across history or current text.

    Uses simple substring matching against known condition names and alias map.
    Picks the longest match to bias towards specific multi-word conditions.
    """
    conditions, alias_map = _build_condition_index()
    def resolve(text: str) -> str | None:
        t = (text or "").lower()
        best: tuple[int, str] | None = None
        # Check aliases first
        for alias, canonical in alias_map.items():
            if alias in t:
                cand = canonical
                if not best or len(cand) > best[0]:
                    best = (len(cand), cand)
        # Check raw condition names
        for cond in conditions:
            if cond in t:
                cand = cond
                if not best or len(cand) > best[0]:
                    best = (len(cand), cand)
        return best[1] if best else None

    # Prefer current text
    found = resolve(current_text)
    if found:
        return found
    # Then scan recent history (last 10 messages, newest first)
    if history:
        for msg in reversed(history[-10:]):
            candidate = resolve(msg.get("message", ""))
            if candidate:
                return candidate
    return None

def rewrite_followup_query(user_query: str, history: list | None) -> str:
    """Rewrite follow-up queries by injecting the recent condition and inferred intent.

    Examples:
      - "what about symptoms?" → "what are <cond> symptoms"
      - "and treatment?" → "how to treat <cond>"
      - "how to prevent it?" → "how to prevent <cond>"
    """
    q = (user_query or "").strip()
    q_lc = q.lower()
    # Quick check: follow-up cues or pronouns
    is_followup = bool(re.search(r"\b(what about|and)\b", q_lc)) or bool(re.search(r"\b(it|this|that)\b", q_lc))
    intent = detect_intent_from_text(q)
    # If the query already names a condition, leave it
    named_cond = detect_recent_condition([], current_text=q)
    if named_cond:
        return q
    if not is_followup and not intent:
        return q
    cond = detect_recent_condition(history or [], current_text="")
    if not cond:
        return q
    # Map intent to canonical form
    if not intent:
        # Try to inherit last user intent from history
        last_intent = None
        if history:
            for msg in reversed(history[-10:]):
                if msg.get("sender") == "user":
                    last_intent = detect_intent_from_text(msg.get("message", ""))
                    if last_intent:
                        break
        intent = last_intent or "information"
    # Build canonical query by intent
    if intent == "treatment":
        return f"how to treat {cond}"
    if intent == "prevention":
        return f"how to prevent {cond}"
    if intent == "symptom":
        return f"what are {cond} symptoms"
    if intent == "cause":
        return f"what causes {cond}"
    # Default information
    return f"what is {cond}"

def extract_medical_conditions_from_dataset():
    """Extract all medical conditions from the dataset for comprehensive coverage"""
    if not os.path.exists(DATA_CSV):
        return set()
    
    df = pd.read_csv(DATA_CSV).fillna("")
    conditions = set()
    
    for _, row in df.iterrows():
        question = row['Question'].lower()
        
        # Extract conditions from common question patterns
        import re
        patterns = [
            r'what is \(are\) (.+?) \?',
            r'what are the symptoms of (.+?) \?',
            r'what are the treatments for (.+?) \?',
            r'what causes (.+?) \?',
            r'how to prevent (.+?) \?',
            r'symptoms of (.+?) \?',
            r'treatments for (.+?) \?',
            r'causes of (.+?) \?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, question)
            for match in matches:
                # Clean condition name
                condition = re.sub(r'[^a-zA-Z\s\-]', ' ', match).strip()
                condition = ' '.join(condition.split())  # Remove extra spaces
                if len(condition) > 3 and not any(stop in condition.split() for stop in ['the', 'and', 'or', 'is', 'are', 'can', 'you', 'may']):
                    conditions.add(condition)
                    # Also add individual parts for compound terms like "Parasites - Schistosomiasis"
                    if ' - ' in condition:
                        parts = condition.split(' - ')
                        for part in parts:
                            part = part.strip()
                            if len(part) > 3:
                                conditions.add(part)
                    # Add individual words for multi-word conditions
                    words = condition.split()
                    for word in words:
                        if len(word) > 4 and word not in ['disease', 'syndrome', 'disorder']:
                            conditions.add(word)
        
        # Also extract individual important medical terms
        medical_terms = ['syndrome', 'disease', 'deficiency', 'dystrophy', 'myopathy', 'neuropathy', 
                        'anemia', 'leukemia', 'cancer', 'diabetes', 'hypertension', 'infection',
                        'malaria', 'fever', 'headache', 'migraine', 'asthma', 'arthritis']
        
        for term in medical_terms:
            if term in question:
                conditions.add(term)
    
    return conditions

def extract_entities_from_dataset():
    """Extract generic entities/topics from Questions across qtypes (not just diseases)."""
    if not os.path.exists(DATA_CSV):
        return set()

    df = pd.read_csv(DATA_CSV).fillna("")
    entities: set[str] = set()

    patterns = [
        r'what is \(are\) (.+?) \?',
        r'what is (.+?) \?',
        r'what are the symptoms of (.+?) \?',
        r'what are the treatments for (.+?) \?',
        r'what causes (.+?) \?',
        r'how to prevent (.+?) \?',
        r'symptoms of (.+?) \?',
        r'treatments for (.+?) \?',
        r'causes of (.+?) \?',
        r'tests for (.+?) \?',
        r'how to diagnose (.+?) \?',
        r'what to do for (.+?) \?',
        r'outlook for (.+?) \?',
        r'stages of (.+?) \?',
        r'who is at risk for (.+?) \?',
    ]

    for _, row in df.iterrows():
        q = str(row.get('Question', '')).lower()
        for pat in patterns:
            m = re.search(pat, q)
            if m:
                ent = re.sub(r'[^a-z\s-]', ' ', m.group(1)).strip()
                ent = ' '.join(ent.split())
                if len(ent) >= 3 and ent not in {'the', 'and', 'or'}:
                    entities.add(ent)

    return entities

# Cache for alias extraction so we only scan the dataset once per process
_ALIAS_CACHE: dict[str, str] | None = None

def _load_aliases_from_dataset() -> dict[str, str]:
    """Build alias→canonical mappings from dataset content.

    Heuristics:
    - Map acronyms in parentheses to their expanded form, e.g.,
      "chronic kidney disease (CKD)" → {"ckd": "chronic kidney disease"}.
    - Map phrases with "also known as/aka/also called" to the left-hand canonical.
    """
    global _ALIAS_CACHE
    if _ALIAS_CACHE is not None:
        return _ALIAS_CACHE

    alias_map: dict[str, str] = {}
    if not os.path.exists(DATA_CSV):
        _ALIAS_CACHE = alias_map
        return alias_map

    df = pd.read_csv(DATA_CSV).fillna("")
    questions = df.get("Question", pd.Series(dtype=str)).astype(str).tolist()

    p_acro = re.compile(r"([A-Za-z][A-Za-z\s]{3,}?)[\s\-]*\(([A-Za-z][A-Za-z0-9]{2,10})\)")
    p_aka = re.compile(r"([A-Za-z][A-Za-z\s]{3,}?)\s+(?:also\s+known\s+as|aka|also\s+called)\s+([A-Za-z][A-Za-z\s]{3,})",
                       re.IGNORECASE)

    for q in questions:
        for m in p_acro.finditer(q):
            canonical = m.group(1).strip().lower()
            acro = m.group(2).strip().lower()
            if len(canonical) >= 4 and 2 <= len(acro) <= 30:
                alias_map[acro] = canonical

        for m in p_aka.finditer(q):
            canonical = m.group(1).strip().lower()
            alias = m.group(2).strip().lower()
            if len(canonical) >= 4 and len(alias) >= 3:
                alias_map[alias] = canonical

    _ALIAS_CACHE = alias_map
    return alias_map

def smart_dataset_lookup(user_query: str, label: str = None):
    """High-precision dataset lookup.

    Intent: prioritize exact and near-exact matches from the cleaned dataset to
    guarantee correctness. In STRICT_MODE, we avoid loose heuristics entirely
    and fall back to downstream semantic/TF-IDF stages for paraphrases.
    """
    if not os.path.exists(DATA_CSV):
        return None
    
    df = pd.read_csv(DATA_CSV).fillna("")
    query_lower = user_query.lower()

    # 0) Highest priority: exact/near-exact match against normalized dataset questions
    # Normalize by lowercasing, removing punctuation, and collapsing whitespace
    import re as _re
    def _normalize_q(text: str) -> str:
        text = text.lower()
        text = _re.sub(r"[^a-z0-9\s]", " ", text)
        return _re.sub(r"\s+", " ", text).strip()

    norm_user_q = _normalize_q(user_query)
    if "__norm_cached__" not in df.columns:
        # Create and cache a normalized column for faster reuse within this process
        df["__norm_cached__"] = df["Question"].astype(str).apply(_normalize_q)

    # Exact normalized match
    exact_matches = df[df["__norm_cached__"] == norm_user_q]
    if not exact_matches.empty:
        if label:
            exact_label = exact_matches[exact_matches["qtype"] == label]
            if not exact_label.empty:
                return exact_label.iloc[0]["Answer"]
        return exact_matches.iloc[0]["Answer"]

    # Near-exact fuzzy normalized match (high cutoff)
    import difflib as _difflib
    all_norm = df["__norm_cached__"].tolist()
    close_norm = _difflib.get_close_matches(norm_user_q, all_norm, n=1, cutoff=0.92)
    if close_norm:
        idx = all_norm.index(close_norm[0])
        # Respect label if provided
        if label:
            # Try to find a nearby row with same normalized text and label
            same_norm = df[df["__norm_cached__"] == close_norm[0]]
            same_norm_label = same_norm[same_norm["qtype"] == label]
            if not same_norm_label.empty:
                return same_norm_label.iloc[0]["Answer"]
        return df.iloc[idx]["Answer"]

    # Get all medical conditions from dataset
    all_conditions = extract_medical_conditions_from_dataset()
    
    # In strict mode, we stop after exact and near-exact matches
    if STRICT_MODE:
        return None

    # Priority 1 (non-strict): Detect ANY medical condition mentioned in the query
    detected_condition = None
    best_match_length = 0
    
    for condition in all_conditions:
        condition_words = condition.lower().split()
        # Check if condition words appear in query
        if len(condition_words) == 1:
            if condition_words[0] in query_lower:
                if len(condition) > best_match_length:
                    detected_condition = condition
                    best_match_length = len(condition)
        else:
            # Multi-word conditions - check if all words present
            if all(word in query_lower for word in condition_words):
                if len(condition) > best_match_length:
                    detected_condition = condition
                    best_match_length = len(condition)
    
    # If we detected a condition, look for relevant entries
    if detected_condition:
        # Create flexible search pattern for the condition
        condition_words = detected_condition.lower().split()
        condition_pattern = '|'.join(condition_words)
        
        condition_mask = df['Question'].str.contains(condition_pattern, case=False, na=False, regex=True)
        condition_df = df[condition_mask]
        
        if not condition_df.empty:
            # If label specified, filter by it first
            if label:
                label_matches = condition_df[condition_df['qtype'] == label]
                if not label_matches.empty:
                    return label_matches.iloc[0]['Answer']
            
            # Intent-based matching
            intent_keywords = {
                'cause': ['cause', 'causes', 'why', 'reason', 'etiology', 'how do you get'],
                'symptom': ['symptom', 'symptoms', 'signs', 'feel', 'have', 'experience'],
                'treatment': ['treat', 'cure', 'therapy', 'medicine', 'medication', 'manage'],
                'prevention': ['prevent', 'avoid', 'stop', 'protect', 'reduce risk'],
                'information': ['what is', 'what are', 'tell me about', 'information']
            }
            
            # Match intent and find corresponding entries
            for intent, keywords in intent_keywords.items():
                if any(keyword in query_lower for keyword in keywords):
                    intent_matches = condition_df[condition_df['qtype'] == intent]
                    if not intent_matches.empty:
                        return intent_matches.iloc[0]['Answer']
            
            # Fallback: return best available entry for this condition
            return condition_df.iloc[0]['Answer']
    
    # Priority 2 (non-strict): Symptom indicator matching ("I have X")
    symptom_indicators = ['i have', 'i feel', 'experiencing', 'suffering from', 'dealing with']
    if any(indicator in query_lower for indicator in symptom_indicators):
        # Extract what they "have"
        for indicator in symptom_indicators:
            if indicator in query_lower:
                after_indicator = query_lower.split(indicator, 1)[1].strip()
                # Remove common words
                symptom_words = [w for w in after_indicator.split() if w not in ['a', 'an', 'the', 'with', 'and']]
                
                if symptom_words:
                    # Look for entries that mention these symptoms
                    for symptom_word in symptom_words:
                        symptom_mask = df['Question'].str.contains(symptom_word, case=False, na=False)
                        symptom_df = df[symptom_mask]
                        
                        if not symptom_df.empty:
                            # Prefer symptom-type entries
                            symptom_type_matches = symptom_df[symptom_df['qtype'] == 'symptom']
                            if not symptom_type_matches.empty:
                                return symptom_type_matches.iloc[0]['Answer']
                            return symptom_df.iloc[0]['Answer']
    
    # Priority 3 (non-strict): Semantic keyword matching across entire dataset
    query_words = [w for w in query_lower.split() if len(w) > 3 and w not in ['what', 'how', 'the', 'are', 'for', 'with']]
    
    if query_words:
        best_matches = []
        for _, row in df.iterrows():
            question_lower = row['Question'].lower()
            answer_lower = row['Answer'].lower()
            
            # Count keyword matches
            question_matches = sum(1 for word in query_words if word in question_lower)
            answer_matches = sum(1 for word in query_words if word in answer_lower)
            total_matches = question_matches + (answer_matches * 0.5)  # Weight question matches higher
            
            if total_matches > 0:
                best_matches.append((total_matches, row))
        
        # Sort by match score and return best
        if best_matches:
            best_matches.sort(key=lambda x: x[0], reverse=True)
            
            # If label specified, prefer matches with that label
            if label:
                label_matches = [match for match in best_matches if match[1]['qtype'] == label]
                if label_matches:
                    return label_matches[0][1]['Answer']
            
            return best_matches[0][1]['Answer']
    
    # Priority 4 (non-strict): Fuzzy matching fallback
    import difflib
    if label:
        df_filtered = df[df["qtype"] == label]
    else:
        df_filtered = df
    
    if df_filtered.empty:
        return None

    questions = df_filtered["Question"].astype(str).tolist()
    norm_questions = [q.strip().lower() for q in questions]
    close = difflib.get_close_matches(query_lower, norm_questions, n=1, cutoff=0.4)  # Even lower cutoff
    
    if close:
        idx = norm_questions.index(close[0])
        return df_filtered["Answer"].iloc[idx]
    
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

def handle_single_keyword_query(query: str, label: str = None) -> str | None:
    """Handle single keyword queries like 'malaria', 'diabetes', 'headache'."""
    if not os.path.exists(DATA_CSV):
        return None
    
    df = pd.read_csv(DATA_CSV).fillna("")
    query_lower = query.strip().lower()
    
    # Check if it's a single word or short phrase (max 3 words)
    words = query_lower.split()
    if len(words) > 3:
        return None
    
    # Get all medical conditions from dataset
    all_conditions = extract_medical_conditions_from_dataset()
    
    # Find matching conditions
    matching_conditions = []
    for condition in all_conditions:
        condition_lower = condition.lower()
        # Exact match
        if condition_lower == query_lower:
            matching_conditions.append((condition, 100))  # Perfect match
        # Partial match - check if query is contained in condition or vice versa
        elif query_lower in condition_lower or condition_lower in query_lower:
            # Calculate similarity score
            import difflib
            similarity = difflib.SequenceMatcher(None, query_lower, condition_lower).ratio()
            if similarity > 0.6:  # 60% similarity threshold
                matching_conditions.append((condition, similarity * 100))
        # Word-level matching for compound terms like "parasites - schistosomiasis"
        elif ' - ' in condition_lower:
            parts = condition_lower.split(' - ')
            for part in parts:
                part = part.strip()
                if query_lower in part or part in query_lower:
                    import difflib
                    similarity = difflib.SequenceMatcher(None, query_lower, part).ratio()
                    if similarity > 0.7:  # Higher threshold for word-level matches
                        matching_conditions.append((condition, similarity * 100))
                        break
    
    if not matching_conditions:
        return None
    
    # Sort by similarity score (highest first)
    matching_conditions.sort(key=lambda x: x[1], reverse=True)
    best_condition = matching_conditions[0][0]
    
    # Search for information about this condition
    condition_words = best_condition.lower().split()
    condition_pattern = '|'.join(condition_words)
    
    condition_mask = df['Question'].str.contains(condition_pattern, case=False, na=False, regex=True)
    condition_df = df[condition_mask]
    
    if condition_df.empty:
        return None
    
    # If label specified, try to find that specific type of information
    if label:
        label_matches = condition_df[condition_df['qtype'] == label]
        if not label_matches.empty:
            return label_matches.iloc[0]['Answer']
    
    # Default to 'information' type if available
    info_matches = condition_df[condition_df['qtype'] == 'information']
    if not info_matches.empty:
        return info_matches.iloc[0]['Answer']
    
    # Fallback to any available answer
    return condition_df.iloc[0]['Answer']

# Unified answer function
def get_answer(user_question: str, label: str = None, context: str = None, history: list = None) -> str:
    # Improve context-dependent queries & follow-ups
    user_question = improve_query_with_context(user_question, context, history)
    user_question = rewrite_followup_query(user_question, history)
    user_question = normalize_intent_phrases(user_question)
    user_question = canonicalize_condition_terms(user_question)
    norm_query = normalize_text(user_question)

    # 0️⃣ Smalltalk check
    smalltalk_resp = check_smalltalk(user_question)
    if smalltalk_resp:
        return smalltalk_resp

    # 0.5️⃣ Single keyword check (for terms like "malaria", "diabetes", "headache")
    single_keyword_ans = handle_single_keyword_query(user_question, label)
    if single_keyword_ans:
        set_cached_answer(norm_query, single_keyword_ans)
        return single_keyword_ans

    # 1️⃣ Cache check with consistency guard
    cached = get_cached_answer(norm_query)
    if cached and is_cache_consistent_with_query(user_question, cached):
        return cached

    # 2️⃣ Smart dataset lookup (prioritizes our comprehensive cleaned data)
    smart_ans = smart_dataset_lookup(user_question, label=label)
    if smart_ans:
        set_cached_answer(norm_query, smart_ans)
        return smart_ans

    # 3️⃣ SVM + TF-IDF pipeline
    ans = qa_lookup_answer(user_question, label, context=context, history=history)
    if ans:
        set_cached_answer(norm_query, ans)
        return ans

    # 4️⃣ FAISS semantic search
    try:
        if _find_best_answers_impl is None:
            raise ImportError("semantic search unavailable")
        results = _find_best_answers_impl(user_question, top_k=5)
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

    # 5️⃣ Disease-specific hardcoded fallback (only for very specific cases)
    disease = get_disease_from_query(user_question)
    intent = None
    for key, kws in INTENT_KEYWORDS.items():
        if any(kw in norm_query for kw in kws):
            intent = key
            break

    if disease and intent and disease == "malaria":
        # Only keep malaria hardcoded as absolute fallback
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

    # 6️⃣ Default fallback
    default = "Sorry, I don't have a specific answer for that right now."
    set_cached_answer(norm_query, default)
    return default
