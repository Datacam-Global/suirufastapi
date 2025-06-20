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
    text = request.get("text")
    if not text or not isinstance(text, str):
        raise HTTPException(status_code=422, detail="A 'text' field of type string is required.")
        
    label, confidence, severity = misinfo_analyzer.predict(text)
    return MisinformationResponse(
        text=text,
        label=label,
        confidence=confidence,
        severity=severity,
        timestamp=datetime.now(),
        explanation=f"Detected as {label} (confidence: {confidence}, severity: {severity})"
    )
