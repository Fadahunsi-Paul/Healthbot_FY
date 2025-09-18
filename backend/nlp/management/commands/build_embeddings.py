# __define-ocg__: Build FAISS index with paraphrase expansion
from django.core.management.base import BaseCommand
import os
import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import faiss
from django.conf import settings
from transformers import pipeline, AutoTokenizer, T5Tokenizer

# Paths
DATA_CSV = os.path.join(settings.BASE_DIR, "api", "dataset", "train_augmented.csv")
FAISS_INDEX_PATH = os.path.join(settings.BASE_DIR, "api", "dataset", "faiss_index.idx")
FAISS_META_PATH = os.path.join(settings.BASE_DIR, "api", "dataset", "faiss_index_meta.json")

# Models
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
PARA_MODEL = "Vamsi/T5_Paraphrase_Paws"

# Params
BATCH_SIZE = 128
PARAPHRASES_PER_Q = 3  # can set 3–5 depending on dataset size


class Command(BaseCommand):
    help = "Expand dataset with paraphrases, build embeddings, and save FAISS index + metadata"

    def handle(self, *args, **options):
        if not os.path.exists(DATA_CSV):
            self.stdout.write(self.style.ERROR(f"Dataset not found at {DATA_CSV}"))
            return

        # Load dataset
        df = pd.read_csv(DATA_CSV).fillna("")
        questions = df["Question"].astype(str).tolist()
        answers = df["Answer"].astype(str).tolist()
        qtypes = df["qtype"].astype(str).tolist() if "qtype" in df.columns else [""] * len(questions)

        self.stdout.write("Loading models...")
        embedder = SentenceTransformer(EMBED_MODEL)
        paraphraser = pipeline(
    "text2text-generation",
    model=PARA_MODEL,
    tokenizer=T5Tokenizer.from_pretrained(PARA_MODEL))


        all_questions, all_answers, all_qtypes = [], [], []

        self.stdout.write("Generating paraphrases...")
        for q, a, t in zip(questions, answers, qtypes):
            try:
                paras = paraphraser(
                    f"paraphrase: {q}",
                    max_length=64,
                    num_return_sequences=PARAPHRASES_PER_Q,
                    temperature=0.7,
                )
                para_texts = [p["generated_text"].strip() for p in paras]
            except Exception:
                para_texts = []

            # Deduplicate + include original
            variants = list(set([q] + para_texts))

            for v in variants:
                all_questions.append(v)
                all_answers.append(a)
                all_qtypes.append(t)

        # Batch encode
        self.stdout.write("Encoding embeddings...")
        all_embs = []
        for i in range(0, len(all_questions), BATCH_SIZE):
            batch = all_questions[i:i + BATCH_SIZE]
            emb = embedder.encode(batch, convert_to_numpy=True)
            all_embs.append(emb)
        embeddings = np.vstack(all_embs).astype("float32")

        # Normalize (cosine similarity)
        faiss.normalize_L2(embeddings)

        # Build FAISS index
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)
        faiss.write_index(index, FAISS_INDEX_PATH)

        # Save metadata
        meta = []
        for q, a, t in zip(all_questions, all_answers, all_qtypes):
            meta.append({"question": q, "answer": a, "qtype": t})
        with open(FAISS_META_PATH, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"FAISS index saved to {FAISS_INDEX_PATH}"))
        self.stdout.write(self.style.SUCCESS(f"Metadata saved to {FAISS_META_PATH}"))
        self.stdout.write(self.style.SUCCESS(f"Total Q variants stored: {len(all_questions)}"))
