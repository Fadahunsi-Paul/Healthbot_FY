# __define-ocg__ Full Training and Save Pipeline
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from imblearn.over_sampling import RandomOverSampler

# 1. Load dataset
df = pd.read_csv("dataset/train.csv")

# 2. Clean rare classes
counts = df['qtype'].value_counts()
rare_classes = counts[counts < 5].index
df = df[~df['qtype'].isin(rare_classes)]  # drop ultra-rare classes

X, y = df['Question'], df['qtype']

# 3. Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words="english", max_features=10000, ngram_range=(1, 2))
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# 5. Oversampling (for balanced training)
ros = RandomOverSampler(random_state=42)
X_train_res, y_train_res = ros.fit_resample(X_train_tfidf, y_train)

# 6. Train SVM
svm = LinearSVC(class_weight="balanced")
svm.fit(X_train_res, y_train_res)

# 7. Save model + vectorizer
joblib.dump(svm, "svm_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")

print("✅ Model and vectorizer saved!")
