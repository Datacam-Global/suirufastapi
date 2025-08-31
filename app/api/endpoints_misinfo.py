from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any
from app.models.misinformation import MisinformationAnalyzer

router = APIRouter()

class MisinformationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Text to analyze for misinformation")

class MisinformationResponse(BaseModel):
    text: str
    label: str
    confidence: float
    severity: str
    timestamp: datetime
    explanation: str

misinfo_analyzer = MisinformationAnalyzer()

@router.post("/analyze/", response_model=MisinformationResponse)
@router.post("/analyze", response_model=MisinformationResponse)
async def analyze_misinformation(request: MisinformationRequest):
    try:
        # Extract text from the request
        text_to_analyze = request.text
        
        # Call OpenAI for misinformation detection
        label, confidence, severity = misinfo_analyzer.predict(text_to_analyze)
        
        return MisinformationResponse(
            text=text_to_analyze,
            label=label,
            confidence=confidence,
            severity=severity,
            timestamp=datetime.now(),
            explanation=f"OpenAI analysis: {label} (confidence: {confidence}, severity: {severity})"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing misinformation: {str(e)}")
