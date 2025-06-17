from fastapi import APIRouter, HTTPException
from schemas.content_schemas import MisinformationRequest, MisinformationResponse
from models.content_analyzer import ContentAnalyzerFactory

router = APIRouter(prefix="/misinformation", tags=["misinformation"])

# Initialize the misinformation analyzer
misinformation_analyzer = ContentAnalyzerFactory.create_misinformation_analyzer()

@router.post("/analyze", response_model=MisinformationResponse)
async def analyze_misinformation(request: MisinformationRequest):
    """
    Analyze text for misinformation content
    """
    try:
        prediction, probability, confidence_level = misinformation_analyzer.predict(request.text)
        details = misinformation_analyzer.get_details()
        
        # Add request metadata to details if provided
        if request.metadata:
            details["request_metadata"] = request.metadata
        
        return MisinformationResponse(
            prediction=prediction,
            probability=probability,
            confidence_level=confidence_level,
            details=details
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing text for misinformation: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Check if misinformation analyzer is working
    """
    return {"status": "healthy", "message": "Misinformation analyzer is ready"}

@router.get("/info")
async def get_analyzer_info():
    """
    Get information about the misinformation analyzer
    """
    return {
        "analyzer_type": "misinformation",
        "model_details": misinformation_analyzer.get_details()
    }