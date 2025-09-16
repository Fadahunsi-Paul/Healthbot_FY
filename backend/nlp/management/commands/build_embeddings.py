# nlp/management/commands/build_embeddings.py
from django.core.management.base import BaseCommand
import os
import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
from django.conf import settings

DATA_CSV = os.path.join(settings.BASE_DIR, "api", "dataset", "train.csv")
FAISS_INDEX_PATH = os.path.join(settings.BASE_DIR, "api", "dataset", "faiss_index.idx")
FAISS_META_PATH = os.path.join(settings.BASE_DIR, "api", "dataset", "faiss_index_meta.json")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 128

class Command(BaseCommand):
    help = "Build embeddings from train.csv and create FAISS index + metadata (including qtype)"

    def handle(self, *args, **options):
        model = SentenceTransformer(MODEL_NAME)

        if not os.path.exists(DATA_CSV):
            self.stdout.write(self.style.ERROR(f"Dataset not found at {DATA_CSV}"))
            return

        df = pd.read_csv(DATA_CSV).fillna("")
        questions = df["Question"].astype(str).tolist()
        answers = df["Answer"].astype(str).tolist()
        qtypes = df["qtype"].astype(str).tolist() if "qtype" in df.columns else [""] * len(questions)

        # Batch encode
        all_embs = []
        for i in range(0, len(questions), BATCH_SIZE):
            batch = questions[i:i+BATCH_SIZE]
            emb = model.encode(batch, convert_to_numpy=True)
            all_embs.append(emb)
        embeddings = np.vstack(all_embs).astype("float32")

        # Normalize (so inner product = cosine similarity)
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)

        faiss.write_index(index, FAISS_INDEX_PATH)

        # Save metadata including qtype
        meta = []
        for q, a, t in zip(questions, answers, qtypes):
            meta.append({"question": q, "answer": a, "qtype": t})
        with open(FAISS_META_PATH, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"FAISS index saved to {FAISS_INDEX_PATH}"))
        self.stdout.write(self.style.SUCCESS(f"Metadata saved to {FAISS_META_PATH}"))
