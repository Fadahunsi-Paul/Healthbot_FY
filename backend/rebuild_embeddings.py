#!/usr/bin/env python3
"""
Simple script to rebuild FAISS embeddings without Django dependencies
"""
import os
import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss

# Configuration
DATA_CSV = "api/dataset/train.csv"
FAISS_INDEX_PATH = "api/dataset/faiss_index.idx"
FAISS_META_PATH = "api/dataset/faiss_index_meta.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 128

def rebuild_embeddings():
    """Rebuild FAISS embeddings from the cleaned dataset"""
    print("🔄 Rebuilding FAISS embeddings...")
    
    # Load model
    print(f"📥 Loading SentenceTransformer model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    
    # Load dataset
    if not os.path.exists(DATA_CSV):
        print(f"❌ Dataset not found: {DATA_CSV}")
        return False
    
    df = pd.read_csv(DATA_CSV).fillna("")
    print(f"📊 Dataset size: {len(df)} rows")
    
    # Check malaria entries
    malaria_mask = df['Question'].str.contains('malaria', case=False, na=False)
    malaria_df = df[malaria_mask]
    print(f"🦟 Malaria entries: {len(malaria_df)}")
    
    # Prepare data
    questions = df["Question"].astype(str).tolist()
    answers = df["Answer"].astype(str).tolist()
    qtypes = df["qtype"].astype(str).tolist() if "qtype" in df.columns else [""] * len(questions)
    
    print(f"📝 Processing {len(questions)} questions...")
    
    # Batch encode questions
    all_embs = []
    for i in range(0, len(questions), BATCH_SIZE):
        batch = questions[i:i+BATCH_SIZE]
        print(f"  Processing batch {i//BATCH_SIZE + 1}/{(len(questions)-1)//BATCH_SIZE + 1}")
        emb = model.encode(batch, convert_to_numpy=True)
        all_embs.append(emb)
    
    embeddings = np.vstack(all_embs).astype("float32")
    print(f"📐 Embeddings shape: {embeddings.shape}")
    
    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    
    # Create FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # Inner product for cosine similarity
    index.add(embeddings)
    
    # Save FAISS index
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"💾 FAISS index saved to: {FAISS_INDEX_PATH}")
    
    # Save metadata
    meta = []
    for q, a, t in zip(questions, answers, qtypes):
        meta.append({"question": q, "answer": a, "qtype": t})
    
    with open(FAISS_META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"📋 Metadata saved to: {FAISS_META_PATH}")
    
    # Test with malaria queries
    test_queries = [
        "What causes malaria?",
        "malaria causes",
        "How do you get malaria?",
        "What are malaria symptoms?"
    ]
    
    print("\n🧪 Testing FAISS search with malaria queries:")
    for query in test_queries:
        query_emb = model.encode([query], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(query_emb)
        
        scores, indices = index.search(query_emb, k=3)
        print(f"\n  Query: '{query}'")
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(meta):
                result = meta[idx]
                print(f"    {i+1}. Score: {score:.3f} | Type: {result['qtype']} | Q: {result['question'][:80]}...")
    
    print(f"\n✅ FAISS embeddings rebuilt successfully!")
    print(f"📊 Total embeddings: {len(embeddings)}")
    return True

if __name__ == "__main__":
    success = rebuild_embeddings()
    if success:
        print("\n🎉 Embedding rebuild completed!")
        print("The AI should now respond better to malaria queries.")
    else:
        print("❌ Embedding rebuild failed!")
