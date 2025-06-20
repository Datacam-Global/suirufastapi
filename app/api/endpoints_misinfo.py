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
async def analyze_misinformation(request: Dict[str, Any]):
    text_data = request.get("text")
    
    if isinstance(text_data, dict):
        text_to_analyze = text_data.get("text")
    elif isinstance(text_data, str):
        text_to_analyze = text_data
    else:
        raise HTTPException(status_code=422, detail="The 'text' field must be a string or an object containing a 'text' string.")

    if not text_to_analyze:
        raise HTTPException(status_code=422, detail="No text to analyze.")
        
    label, confidence, severity = misinfo_analyzer.predict(text_to_analyze)
    return MisinformationResponse(
        text=text_to_analyze,
        label=label,
        confidence=confidence,
        severity=severity,
        timestamp=datetime.now(),
        explanation=f"Detected as {label} (confidence: {confidence}, severity: {severity})"
    )
