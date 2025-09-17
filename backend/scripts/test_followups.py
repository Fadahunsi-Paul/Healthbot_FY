import os
import sys
import re

# Ensure project root on sys.path for Django imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django  # noqa: E402

django.setup()

from nlp.service.services import get_answer  # noqa: E402
import pandas as pd  # noqa: E402


BASE = os.path.dirname(os.path.dirname(__file__))
DATA_CSV = os.path.join(BASE, 'api', 'dataset', 'train.csv')


def extract_entity(q: str) -> str | None:
    pats = [
        r'what is \(are\) (.+?) \?', r'what is (.+?) \?', r'what are the symptoms of (.+?) \?',
        r'what are the treatments for (.+?) \?', r'what causes (.+?) \?', r'how to prevent (.+?) \?',
        r'symptoms of (.+?) \?', r'treatments for (.+?) \?', r'causes of (.+?) \?', r'tests for (.+?) \?',
        r'how to diagnose (.+?) \?', r'what to do for (.+?) \?', r'outlook for (.+?) \?', r'stages of (.+?) \?'
    ]
    ql = (q or '').lower()
    for p in pats:
        m = re.search(p, ql)
        if m:
            ent = re.sub(r'[^a-z\s-]', ' ', m.group(1)).strip()
            ent = ' '.join(ent.split())
            if len(ent) >= 3:
                return ent
    return None


def main(max_topics: int = 8):
    df = pd.read_csv(DATA_CSV).fillna('')
    topics = []
    for _, row in df.iterrows():
        ent = extract_entity(row['Question'])
        if ent:
            topics.append((row['qtype'], ent))
    # Deduplicate by entity string
    seen = set()
    uniq = []
    for qt, ent in topics:
        if ent not in seen:
            uniq.append((qt, ent))
            seen.add(ent)
        if len(uniq) >= max_topics:
            break

    total = 0
    passed = 0
    for qt, ent in uniq:
        history = []
        base_q = f"what is {ent}"
        a1 = get_answer(base_q, label='information', history=history)
        history.append({"sender": "user", "message": base_q})
        history.append({"sender": "bot", "message": a1 or ''})

        scenarios = [
            ("what about symptoms?", "symptom"),
            ("and treatment?", "treatment"),
            ("how to prevent it?", "prevention"),
            ("what about tests?", "exams and tests"),
        ]
        print(f"\nTopic: {ent}")
        print(f"  Base: {bool(a1 and a1.strip() and a1.strip().lower() != "i don't know")}")
        for fq, lab in scenarios:
            total += 1
            ans = get_answer(fq, label=lab, history=history)
            ok = bool(ans and ans.strip() and ans.strip().lower() not in {"i don't know", "sorry, i don't have a specific answer for that right now."})
            if ok:
                passed += 1
            print(f"  Follow-up [{lab}]: {ok}")
            history.append({"sender": "user", "message": fq})
            history.append({"sender": "bot", "message": ans or ''})

    print(f"\nFollow-up success: {passed}/{total} ( { (passed/total*100):.1f}% )")


if __name__ == '__main__':
    main()


