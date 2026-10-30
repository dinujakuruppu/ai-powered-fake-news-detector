
import csv
from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

# Define paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)

# Convert LIAR labels into binary classes.
# Exclude ambiguous "half-true" statements.
label_map = {
    "false": "FAKE",
    "pants-fire": "FAKE",
    "barely-true": "FAKE",
    "mostly-true": "REAL",
    "true": "REAL"
}

def load_dataset(filename):
    df = pd.read_csv(
        DATA_DIR / filename,
        sep="\t",
        header=None,
        usecols=[1, 2],
        quoting=csv.QUOTE_NONE
    )

    df.columns = ["original_label", "text"]

    df["label"] = (
        df["original_label"]
        .str.strip()
        .str.lower()
        .map(label_map)
    )

    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"] != ""]

    return df

# Load training and validation data
train_data = load_dataset("train.tsv")
valid_data = load_dataset("valid.tsv")

print("Training samples:", len(train_data))
print("Validation samples:", len(valid_data))

# Build machine learning pipeline
model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            stop_words="english",
            max_features=50000,
            ngram_range=(1, 2)
        )
    ),
    (
        "classifier",
        LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )
    )
])

# Train AI model
print("\nTraining AI Model...")

model.fit(
    train_data["text"],
    train_data["label"]
)

print("Model Training Completed!")

# Evaluate on validation dataset
predictions = model.predict(valid_data["text"])

accuracy = accuracy_score(
    valid_data["label"],
    predictions
)

print("\nValidation Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(
    classification_report(
        valid_data["label"],
        predictions,
        zero_division=0
    )
)

# Save trained model
model_path = MODEL_DIR / "fake_news_model.joblib"

joblib.dump(model, model_path)

print("\nAI Model Saved Successfully!")
print("Model location:", model_path)
