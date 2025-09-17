import os
import random
import re
import sys
from difflib import SequenceMatcher

import pandas as pd


# Ensure Django settings are available
# Add project root (parent of this scripts directory) to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django  # noqa: E402

django.setup()

from nlp.service.services import get_answer as unified_get_answer  # noqa: E402


def normalize(text: str) -> str:
    if text is None:
        return ""
    text = re.sub(r"\s+", " ", text.strip().lower())
    # remove trailing punctuation differences
    text = re.sub(r"[\s\-–—]*$", "", text)
    return text


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


PARAPHRASE_TEMPLATES = {
    "cause": [
        "what causes {cond}?",
        "how do you get {cond}?",
        "why does {cond} happen?",
        "reasons for {cond}?",
    ],
    "symptom": [
        "what are the symptoms of {cond}?",
        "how does {cond} feel?",
        "signs of {cond}?",
    ],
    "treatment": [
        "how to treat {cond}?",
        "treatment for {cond}?",
        "how do you cure {cond}?",
        "management of {cond}?",
    ],
    "prevention": [
        "how to prevent {cond}?",
        "ways to avoid {cond}?",
        "how can I reduce risk of {cond}?",
    ],
    "information": [
        "what is {cond}?",
        "tell me about {cond}",
        "give information on {cond}",
    ],
}


def make_paraphrases(qtype: str, condition: str) -> list[str]:
    templates = PARAPHRASE_TEMPLATES.get(qtype, [])
    return [t.format(cond=condition) for t in templates]


def main(sample_per_condition: int = 4, max_total: int = 60):
    df = pd.read_csv("api/dataset/train.csv").fillna("")

    # Use a few frequent conditions by heuristic word extraction from questions
    # and prefer common ones
    preferred_conditions = [
        "malaria",
        "diabetes",
        "asthma",
        "cancer",
        "kidney disease",
        "fever",
        "hypertension",
        "headache",
    ]

    tests = []
    for cond in preferred_conditions:
        cond_df = df[df["Question"].str.contains(cond, case=False, na=False)]
        if cond_df.empty:
            continue
        cond_df = cond_df.sample(min(sample_per_condition, len(cond_df)), random_state=42)
        for _, row in cond_df.iterrows():
            tests.append({
                "condition": cond,
                "qtype": row.get("qtype", ""),
                "question": row["Question"],
                "answer": row["Answer"],
            })

    if not tests:
        print("No tests could be constructed from dataset.")
        sys.exit(1)

    random.shuffle(tests)
    tests = tests[:max_total]

    exact_ok = 0
    paraphrase_ok = 0
    total_exact = 0
    total_para = 0
    examples = []

    for t in tests:
        q = t["question"]
        gt = t["answer"]
        label = t.get("qtype") or None

        # Exact question
        total_exact += 1
        pred = unified_get_answer(q, label=label)
        if pred and (normalize(pred) == normalize(gt) or similar(pred, gt) >= 0.9):
            exact_ok += 1
        else:
            examples.append({
                "type": "exact",
                "q": q,
                "label": label,
                "pred": pred,
                "gt": gt,
            })

        # Paraphrases if we can extract a condition from the question
        # Simple heuristic: condition is the chosen preferred condition token
        cond = t["condition"]
        paraphrases = make_paraphrases(label, cond)
        for pq in paraphrases:
            total_para += 1
            p_pred = unified_get_answer(pq, label=label)
            if p_pred and (normalize(p_pred) == normalize(gt) or similar(p_pred, gt) >= 0.9):
                paraphrase_ok += 1
            else:
                if len(examples) < 8:  # cap examples
                    examples.append({
                        "type": "paraphrase",
                        "q": pq,
                        "label": label,
                        "pred": p_pred,
                        "gt": gt,
                    })

    print("\n=== Dataset QA Sanity Check ===")
    print(f"Exact matches: {exact_ok}/{total_exact} ( {exact_ok/total_exact:.1%} )")
    if total_para:
        print(f"Paraphrase matches: {paraphrase_ok}/{total_para} ( {paraphrase_ok/total_para:.1%} )")

    if examples:
        print("\nExamples (showing up to 8):")
        for ex in examples:
            print("-", ex["type"], "|", ex["label"], "\n  Q:", ex["q"], "\n  ▶ Pred:", ex["pred"], "\n  ✓ GT:", ex["gt"])


if __name__ == "__main__":
    main()


