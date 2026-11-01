
from pathlib import Path
import joblib

BASE_DIR = Path(__file__).resolve().parent

model = joblib.load(
    BASE_DIR / "models" / "fake_news_model.joblib"
)

print("AI Fake News Detector")
print("---------------------")

news = input("Enter news text: ").strip()

if not news:
    print("Please enter some text.")
else:
    prediction = model.predict([news])[0]

    print("Model Prediction:", prediction)
    print("Note: This is not a verified fact-check.")
