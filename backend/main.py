
from pathlib import Path
from contextlib import asynccontextmanager
import os
import joblib
from url_analyzer import router as url_router
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prediction_service import predict_with_confidence
from fact_check import router as fact_check_router



# AI Model Path
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "fake_news_model.joblib"


# Load AI Model
@asynccontextmanager
async def lifespan(app: FastAPI):

    if not MODEL_PATH.exists():
        raise RuntimeError(
            "AI Model not found. Train the model first."
        )

    app.state.model = joblib.load(MODEL_PATH)

    print("Fake News AI Model Loaded Successfully!")

    yield


# Create FastAPI Application
app = FastAPI(
    title="AI Fake News Detector",
    version="1.0.0",
    description="AI Powered Fake News Detection API",
    lifespan=lifespan
)


# CORS Configuration

# Allowed frontend domains
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Production frontend URL
production_frontend = os.getenv(
    "FRONTEND_URL", ""
).rstrip("/")

if production_frontend:
    allowed_origins.append(production_frontend)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)



# Add the URL Analyzer router
app.include_router(url_router)
app.include_router(fact_check_router)

# Request Model
class NewsRequest(BaseModel):
    text: str = Field(min_length=10)


# Home Endpoint
@app.get("/")
def home():
    return {
        "message": "Fake News Detector API Running",
        "status": "success"
    }


# AI Prediction Endpoint

@app.post("/api/predict")
def predict_news(request: NewsRequest):

    news_text = request.text.strip()

    if len(news_text) < 10:
        raise HTTPException(
            status_code=400,
            detail="News text must contain at least 10 characters."
        )

    model = app.state.model

    result = predict_with_confidence(
        model,
        news_text
    )

    return {
        "news": news_text,
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "status": "success",
        "note": (
            "Model probability only. "
            "Not a verified fact-check."
        )
    }
