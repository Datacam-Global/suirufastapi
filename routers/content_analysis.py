from fastapi import APIRouter, HTTPException
from schemas.content_schemas import ContentRequest, GeneralContentResponse, ContentType
from models.content_analyzer import ContentAnalyzerFactory
import os

router = APIRouter(prefix="/content", tags=["content-analysis"])

# Initialize analyzers
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    hate_speech_analyzer = ContentAnalyzerFactory.create_hate_speech_analyzer(BASE_DIR)
except Exception as e:
    hate_speech_analyzer = None
    print(f"Failed to load hate speech model: {e}")

misinformation_analyzer = ContentAnalyzerFactory.create_misinformation_analyzer()

@router.post("/analyze", response_model=GeneralContentResponse)
async def analyze_content(request: ContentRequest):
    """
    Analyze content for either hate speech or misinformation based on content_type
    """
    try:
        if request.content_type == ContentType.HATE_SPEECH:
            if hate_speech_analyzer is None:
                raise HTTPException(
                    status_code=500,
                    detail="Hate speech analyzer not available. Model files may be missing."
                )
            analyzer = hate_speech_analyzer
        
        elif request.content_type == ContentType.MISINFORMATION:
            analyzer = misinformation_analyzer
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported content type: {request.content_type}"
            )
        
        prediction, probability, confidence_level = analyzer.predict(request.text)
        analysis_details = analyzer.get_details()
        
        # Add request metadata to analysis details if provided
        if request.metadata:
            analysis_details["request_metadata"] = request.metadata
        
        return GeneralContentResponse(
            content_type=request.content_type,
            prediction=prediction,
            probability=probability,
            confidence_level=confidence_level,
            analysis_details=analysis_details
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing content: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Check the health of all content analyzers
    """
    health_status = {
        "hate_speech": "healthy" if hate_speech_analyzer is not None else "unhealthy",
        "misinformation": "healthy",
        "overall": "healthy" if hate_speech_analyzer is not None else "partial"
    }
    
    return {
        "status": health_status["overall"],
        "analyzers": health_status,
        "message": "Content analysis service status"
    }

@router.get("/supported-types")
async def get_supported_types():
    """
    Get list of supported content analysis types
    """
    return {
        "supported_types": [
            {
                "type": "hate_speech",
                "available": hate_speech_analyzer is not None,
                "description": "Detect hate speech in text content"
            },
            {
                "type": "misinformation",
                "available": True,
                "description": "Detect misinformation in text content"
            }
        ]
    }