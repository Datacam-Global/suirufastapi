from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routers import hate_speech, misinformation, content_analysis
from schemas.content_schemas import ErrorResponse

app = FastAPI(
    title="Content Analysis API",
    description="API for detecting hate speech and misinformation in text content",
    version="1.0.0"
)

# Add CORS middleware to allow requests from Django backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://server.sui-ru.com",
        "http://server.sui-ru.com", 
        "http://localhost:8000",  # For local Django development
        "http://127.0.0.1:8000",  # For local Django development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(hate_speech.router)
app.include_router(misinformation.router)
app.include_router(content_analysis.router)

# Legacy endpoint for backward compatibility
class TweetRequest(BaseModel):
    text: str

class PredictionResponse(BaseModel):
    prediction: str
    probability: float

# Load model and vectorizer for legacy endpoint
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    model = joblib.load(os.path.join(BASE_DIR, "twitter_hate_model.joblib"))
    vectorizer = joblib.load(os.path.join(BASE_DIR, "twitter_hate_vectorizer.joblib"))
    legacy_model_available = True
except Exception as e:
    print(f"Legacy model loading failed: {e}")
    legacy_model_available = False

@app.post("/predict", response_model=PredictionResponse)
def predict(request: TweetRequest):
    """Legacy endpoint for hate speech prediction"""
    if not legacy_model_available:
        raise HTTPException(
            status_code=500,
            detail="Legacy model not available. Use /hate-speech/analyze endpoint instead."
        )
    
    text = request.text.lower()
    X = vectorizer.transform([text])
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0][1]  # Probability for class 1 (hate speech)
    if 0.3 < proba < 0.5:
        prediction = "likely_hate_speech"
    else:
        prediction = "hate_speech" if pred == 1 else "no_hate_speech"
    return PredictionResponse(prediction=prediction, probability=proba)

@app.get("/")
def read_root():
    return {
        "message": "Content Analysis API is running",
        "services": {
            "hate_speech": "/hate-speech/analyze",
            "misinformation": "/misinformation/analyze", 
            "general_analysis": "/content/analyze"
        },
        "health_checks": {
            "hate_speech": "/hate-speech/health",
            "misinformation": "/misinformation/health",
            "general": "/content/health"
        },
        "legacy_endpoint": "/predict (deprecated, use specific endpoints)"
    }

@app.get("/health")
def health_check():
    """Overall health check for the API"""
    return {
        "status": "healthy",
        "message": "Content Analysis API is operational",
        "legacy_model": "available" if legacy_model_available else "unavailable"
    }
