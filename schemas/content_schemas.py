from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class ContentType(str, Enum):
    HATE_SPEECH = "hate_speech"
    MISINFORMATION = "misinformation"

class ContentRequest(BaseModel):
    text: str
    content_type: ContentType
    metadata: Optional[Dict[str, Any]] = None

class HateSpeechRequest(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = None

class MisinformationRequest(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = None

class HateSpeechResponse(BaseModel):
    prediction: str
    probability: float
    confidence_level: str
    details: Optional[Dict[str, Any]] = None

class MisinformationResponse(BaseModel):
    prediction: str
    probability: float
    confidence_level: str
    details: Optional[Dict[str, Any]] = None

class GeneralContentResponse(BaseModel):
    content_type: ContentType
    prediction: str
    probability: float
    confidence_level: str
    analysis_details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None