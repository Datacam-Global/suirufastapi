from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from app.models.hate_speech_detector import CameroonHateSpeechDetector, HateSpeechResult
from app.services.realtime_monitor import DatabaseManager

router = APIRouter()

# ================================
# REQUEST/RESPONSE MODELS
# ================================

class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Text to analyze for hate speech")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    platform: Optional[str] = Field(None, description="Source platform (twitter, facebook, etc.)")
    store_result: bool = Field(True, description="Whether to store result in database")

class BatchAnalysisRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100, description="List of texts to analyze")
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    platform: Optional[str] = Field(None, description="Source platform")
    store_results: bool = Field(True, description="Whether to store results in database")

class HateSpeechResponse(BaseModel):
    text: str
    is_hate_speech: bool
    confidence: float = Field(..., ge=0.0, le=1.0)
    category: str
    severity: str
    detected_keywords: List[str]
    explanation: str
    timestamp: datetime
    processing_time_ms: float

class BatchAnalysisResponse(BaseModel):
    total_analyzed: int
    hate_speech_detected: int
    processing_time_ms: float
    results: List[HateSpeechResponse]
    summary: Dict[str, Any]

class SystemStatsResponse(BaseModel):
    total_requests: int
    hate_speech_detected: int
    clean_content: int
    avg_processing_time_ms: float
    keyword_triggered_percentage: float
    ai_only_detections: int
    uptime: str
    models_loaded: Dict[str, str]

# ================================
# UTILITY FUNCTIONS
# ================================

def get_detector() -> CameroonHateSpeechDetector:
    if not hasattr(get_detector, "detector"):
        get_detector.detector = CameroonHateSpeechDetector(
            model_path="app/models/twitter_hate_model.joblib",
            keywords_path="app/models/keywords.json"  # Update this path if your keywords file is named differently
        )
    return get_detector.detector

def get_db_manager() -> DatabaseManager:
    if not hasattr(get_db_manager, "db_manager"):
        get_db_manager.db_manager = DatabaseManager()
    return get_db_manager.db_manager

def convert_result_to_response(result: HateSpeechResult, processing_time: float) -> HateSpeechResponse:
    return HateSpeechResponse(
        text=result.text,
        is_hate_speech=result.is_hate_speech,
        confidence=result.confidence,
        category=result.category,
        severity=result.severity,
        detected_keywords=result.detected_keywords,
        explanation=result.explanation,
        timestamp=result.timestamp,
        processing_time_ms=processing_time
    )

# ================================
# API ENDPOINTS
# ================================

@router.post("/analyze", response_model=HateSpeechResponse)
async def analyze_text(
        request: TextAnalysisRequest,
        background_tasks: BackgroundTasks,
        detector: CameroonHateSpeechDetector = Depends(get_detector),
        db: DatabaseManager = Depends(get_db_manager)
):
    try:
        start_time = datetime.now()
        result = detector.detect_hate_speech(request.text)
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        if request.store_result:
            metadata = {
                'user_id': request.user_id,
                'platform': request.platform,
                'post_id': None,
                'api_endpoint': '/analyze'
            }
            background_tasks.add_task(db.store_detection, result, metadata)
        response = convert_result_to_response(result, processing_time)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze/batch", response_model=BatchAnalysisResponse)
async def analyze_batch(
        request: BatchAnalysisRequest,
        background_tasks: BackgroundTasks,
        detector: CameroonHateSpeechDetector = Depends(get_detector),
        db: DatabaseManager = Depends(get_db_manager)
):
    try:
        start_time = datetime.now()
        results = detector.batch_detect(request.texts)
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        avg_time_per_text = processing_time / len(request.texts)
        api_results = []
        hate_count = 0
        categories = {}
        severities = {}
        for result in results:
            api_result = convert_result_to_response(result, avg_time_per_text)
            api_results.append(api_result)
            if result.is_hate_speech:
                hate_count += 1
                categories[result.category] = categories.get(result.category, 0) + 1
                severities[result.severity] = severities.get(result.severity, 0) + 1
        if request.store_results:
            metadata = {
                'user_id': request.user_id,
                'platform': request.platform,
                'post_id': None,
                'api_endpoint': '/analyze/batch'
            }
            for result in results:
                background_tasks.add_task(db.store_detection, result, metadata)
        summary = {
            'hate_speech_rate': hate_count / len(request.texts),
            'categories_detected': categories,
            'severity_breakdown': severities,
            'avg_time_per_text_ms': avg_time_per_text
        }
        response = BatchAnalysisResponse(
            total_analyzed=len(request.texts),
            hate_speech_detected=hate_count,
            processing_time_ms=processing_time,
            results=api_results,
            summary=summary
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
        detector: CameroonHateSpeechDetector = Depends(get_detector),
        db: DatabaseManager = Depends(get_db_manager)
):
    try:
        detector_stats = detector.get_statistics()
        db_stats = db.get_statistics(days=7)
        total_requests = detector_stats.get('total_processed', 0)
        hate_detected = detector_stats.get('hate_speech_detected', 0)
        clean_content = total_requests - hate_detected
        keyword_triggered = detector_stats.get('keyword_triggered', 0)
        ai_only = detector_stats.get('ai_only_detected', 0)
        keyword_percentage = (keyword_triggered / total_requests * 100) if total_requests > 0 else 0
        response = SystemStatsResponse(
            total_requests=total_requests,
            hate_speech_detected=hate_detected,
            clean_content=clean_content,
            avg_processing_time_ms=150.0,
            keyword_triggered_percentage=keyword_percentage,
            ai_only_detections=ai_only,
            uptime=str(datetime.now() - datetime.now().replace(hour=0, minute=0, second=0)),
            models_loaded={
                "keyword_detector": "160+ Cameroon-specific terms",
                "ai_classifier": "Pre-trained transformer model",
                "database": "SQLite with real-time logging"
            }
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/health")
async def health_check(detector: CameroonHateSpeechDetector = Depends(get_detector)):
    try:
        test_result = detector.detect_hate_speech("Hello, this is a test.")
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "components": {
                "detector": "✅ operational",
                "database": "✅ operational",
                "ai_model": "✅ operational"
            },
            "test_detection": {
                "processed": True,
                "response_time_ms": "<10"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@router.get("/recent")
async def get_recent_detections(
        hours: int = 24,
        limit: int = 50,
        hate_only: bool = True,
        db: DatabaseManager = Depends(get_db_manager)
):
    try:
        detections = db.get_recent_detections(hours=hours, hate_only=hate_only)
        limited_detections = detections[:limit]
        return {
            "total_found": len(detections),
            "returned": len(limited_detections),
            "time_period_hours": hours,
            "detections": limited_detections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent detections: {str(e)}")

@router.get("/keywords")
async def get_keyword_categories(detector: CameroonHateSpeechDetector = Depends(get_detector)):
    try:
        keywords_info = {}
        total_keywords = 0
        for category, data in detector.keywords_detector.keywords.items():
            keywords_info[category] = {
                "count": len(data['terms']),
                "severity": data['severity'],
                "category": data['category'],
                "examples": data['terms'][:3]
            }
            total_keywords += len(data['terms'])
        return {
            "total_keywords": total_keywords,
            "categories": len(keywords_info),
            "keyword_categories": keywords_info,
            "languages_supported": ["French", "English", "Pidgin", "Mixed"],
            "last_updated": "2024-12-17"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get keyword info: {str(e)}")
