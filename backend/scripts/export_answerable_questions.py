import os
import re
import csv
import pandas as pd

BASE = os.path.dirname(os.path.dirname(__file__))
DATA_CSV = os.path.join(BASE, 'api', 'dataset', 'train.csv')
OUT_CSV = os.path.join(BASE, 'exports', 'answerable_questions.csv')

# Paraphrase templates aligned with services.py normalization
CAUSE_TEMPLATES = [
    'what causes {cond}?',
    'how do you get {cond}?',
    'reasons for {cond}?',
]
SYMPTOM_TEMPLATES = [
    'what are the symptoms of {cond}?',
    'signs of {cond}?',
    'how does {cond} feel?',
]
TREATMENT_TEMPLATES = [
    'how to treat {cond}?',
    'treatment for {cond}?',
    'how do you cure {cond}?',
    'management of {cond}?',
]
PREVENTION_TEMPLATES = [
    'how to prevent {cond}?',
    'ways to avoid {cond}?',
    'how can I reduce risk of {cond}?',
]
INFO_TEMPLATES = [
    'what is {cond}?',
    'tell me about {cond}',
    'give information on {cond}',
]

INTENT_TO_TEMPLATES = {
    'cause': CAUSE_TEMPLATES,
    'symptom': SYMPTOM_TEMPLATES,
    'treatment': TREATMENT_TEMPLATES,
    'prevention': PREVENTION_TEMPLATES,
    'information': INFO_TEMPLATES,
}

# Simple condition extractor mirroring services.py
COND_PATTERNS = [
    r'what is \(are\) (.+?) \?',
    r'what are the symptoms of (.+?) \?',
    r'what are the treatments for (.+?) \?',
    r'what causes (.+?) \?',
    r'how to prevent (.+?) \?',
    r'symptoms of (.+?) \?',
    r'treatments for (.+?) \?',
    r'causes of (.+?) \?',
]


def extract_condition(q: str) -> str | None:
    ql = q.lower()
    for pat in COND_PATTERNS:
        m = re.search(pat, ql)
        if m:
            cond = re.sub(r'[^a-z\s-]', ' ', m.group(1)).strip()
            cond = re.sub(r'\s+', ' ', cond)
            if len(cond) >= 3:
                return cond
    # fallback: last noun-ish phrase (very light)
    tokens = [t for t in re.findall(r'[a-z]{3,}', ql)]
    if tokens:
        return ' '.join(tokens[-2:]) if len(tokens) >= 2 else tokens[-1]
    return None


def main():
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    df = pd.read_csv(DATA_CSV).fillna('')

    rows = []
    seen = set()

    for _, row in df.iterrows():
        q = str(row['Question'])
        a = str(row['Answer'])
        intent = str(row.get('qtype', 'information'))
        cond = extract_condition(q) or ''
        # Always include the original
        key = (q.strip().lower(), intent)
        if key not in seen:
            rows.append(['original', intent, q, cond, a])
            seen.add(key)
        # Paraphrases for recognized intents
        templates = INTENT_TO_TEMPLATES.get(intent, [])
        if cond and templates:
            for t in templates:
                phr = t.format(cond=cond)
                pkey = (phr.strip().lower(), intent)
                if pkey not in seen:
                    rows.append(['paraphrase', intent, phr, cond, a])
                    seen.add(pkey)

    with open(OUT_CSV, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['type', 'qtype', 'question', 'condition', 'answer'])
        w.writerows(rows)

    print(f'Wrote {len(rows)} rows to {OUT_CSV}')


if __name__ == '__main__':
    main()
