# __define-ocg__ Full Training and Save Pipeline
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report
from imblearn.over_sampling import RandomOverSampler

# 1. Load dataset
df = pd.read_csv("dataset/train.csv")
print(f"📊 Original dataset size: {len(df)} rows")

# Check malaria entries
malaria_mask = df['Question'].str.contains('malaria', case=False, na=False)
malaria_df = df[malaria_mask]
print(f"🦟 Malaria entries: {len(malaria_df)}")
print("📋 Malaria question types:")
print(malaria_df['qtype'].value_counts().to_dict())

# 2. Clean rare classes
counts = df['qtype'].value_counts()
rare_classes = counts[counts < 5].index
df = df[~df['qtype'].isin(rare_classes)]  # drop ultra-rare classes
print(f"🧹 After removing rare classes: {len(df)} rows")

X, y = df['Question'], df['qtype']

# 3. Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 4. TF-IDF Vectorizer
vectorizer = TfidfVectorizer(
    stop_words="english", 
    max_features=10000, 
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95
)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# 5. Oversampling (for balanced training)
ros = RandomOverSampler(random_state=42)
X_train_res, y_train_res = ros.fit_resample(X_train_tfidf, y_train)
print(f"📈 Training samples after oversampling: {X_train_res.shape[0]}")

# 6. Train SVM
svm = LinearSVC(class_weight="balanced", random_state=42, max_iter=2000)
svm.fit(X_train_res, y_train_res)

# 7. Evaluate
y_pred = svm.predict(X_test_tfidf)
print("\n📊 Classification Report:")
print(classification_report(y_test, y_pred))

# Test malaria classification specifically
test_queries = [
    "What causes malaria?",
    "How do you get malaria?", 
    "What are malaria symptoms?",
    "How to treat malaria?",
    "How to prevent malaria?",
    "What is malaria?"
]

print("\n🧪 Testing malaria classifications:")
for query in test_queries:
    query_vec = vectorizer.transform([query])
    pred = svm.predict(query_vec)[0]
    confidence = max(svm.decision_function(query_vec)[0])
    print(f"  '{query}' → {pred} (confidence: {confidence:.2f})")

# 8. Save model + vectorizer
joblib.dump(svm, "svm_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")

print("\n✅ Model and vectorizer saved!")
