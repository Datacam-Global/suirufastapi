from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime
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

@router.post("/analyze", response_model=MisinformationResponse)
async def analyze_misinformation(request: MisinformationRequest):
    label, confidence, severity = misinfo_analyzer.predict(request.text)
    return MisinformationResponse(
        text=request.text,
        label=label,
        confidence=confidence,
        severity=severity,
        timestamp=datetime.now(),
        explanation=f"Detected as {label} (confidence: {confidence}, severity: {severity})"
    )
