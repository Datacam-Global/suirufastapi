from fastapi import APIRouter, HTTPException
from schemas.content_schemas import HateSpeechRequest, HateSpeechResponse
from models.content_analyzer import ContentAnalyzerFactory
import os

router = APIRouter(prefix="/hate-speech", tags=["hate-speech"])

# Initialize the hate speech analyzer
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
try:
    hate_speech_analyzer = ContentAnalyzerFactory.create_hate_speech_analyzer(BASE_DIR)
except Exception as e:
    hate_speech_analyzer = None
    print(f"Failed to load hate speech model: {e}")

@router.post("/analyze", response_model=HateSpeechResponse)
async def analyze_hate_speech(request: HateSpeechRequest):
    """
    Analyze text for hate speech content
    """
    if hate_speech_analyzer is None:
        raise HTTPException(
            status_code=500, 
            detail="Hate speech analyzer not available. Model files may be missing."
        )
    
    try:
        prediction, probability, confidence_level = hate_speech_analyzer.predict(request.text)
        details = hate_speech_analyzer.get_details()
        
        # Add request metadata to details if provided
        if request.metadata:
            details["request_metadata"] = request.metadata
        
        return HateSpeechResponse(
            prediction=prediction,
            probability=probability,
            confidence_level=confidence_level,
            details=details
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing text for hate speech: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Check if hate speech analyzer is working
    """
    if hate_speech_analyzer is None:
        return {"status": "unhealthy", "message": "Model not loaded"}
    
    return {"status": "healthy", "message": "Hate speech analyzer is ready"}

@router.get("/info")
async def get_analyzer_info():
    """
    Get information about the hate speech analyzer
    """
    if hate_speech_analyzer is None:
        raise HTTPException(
            status_code=500,
            detail="Hate speech analyzer not available"
        )
    
    return {
        "analyzer_type": "hate_speech",
        "model_details": hate_speech_analyzer.get_details()
    }