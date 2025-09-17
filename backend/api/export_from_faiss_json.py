import json
import csv
import os

SRC_JSON = os.path.join("api", "dataset", "faiss_index_meta.json")
OUT_CSV = os.path.join("api", "dataset", "train.csv")

# The FAISS meta is expected to be a list of records or an object with 'items'
# Each item should have keys like 'question', 'qtype' (or 'label'), and 'answer'

def extract_rows(meta_item):
    q = meta_item.get("question") or meta_item.get("Question") or meta_item.get("q")
    a = meta_item.get("answer") or meta_item.get("Answer") or meta_item.get("a")
    t = meta_item.get("qtype") or meta_item.get("label") or meta_item.get("intent")
    if not (q and a):
        return None
    if not t:
        t = "information"
    return [q, t, a]


def main():
    if not os.path.exists(SRC_JSON):
        raise SystemExit(f"Source JSON not found: {SRC_JSON}")

    with open(SRC_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        items = data.get("items") or data.get("records") or data.get("data") or []
        if not items and "vectors" in data:
            items = [v.get("meta", {}) for v in data["vectors"] if isinstance(v, dict)]
    elif isinstance(data, list):
        items = data
    else:
        items = []

    rows = []
    for it in items:
        if not isinstance(it, dict):
            continue
        # Meta nesting
        meta = it.get("meta") if isinstance(it.get("meta"), dict) else it
        row = extract_rows(meta)
        if row:
            rows.append(row)

    if not rows:
        raise SystemExit("No rows extracted from FAISS meta JSON.")

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "qtype", "Answer"]) 
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
