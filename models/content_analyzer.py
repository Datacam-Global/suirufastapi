import joblib
import os
from typing import Tuple, Dict, Any
from abc import ABC, abstractmethod

class BaseContentAnalyzer(ABC):
    """Base class for content analyzers"""
    
    @abstractmethod
    def predict(self, text: str) -> Tuple[str, float, str]:
        """
        Predict content classification
        Returns: (prediction, probability, confidence_level)
        """
        pass
    
    @abstractmethod
    def get_details(self) -> Dict[str, Any]:
        """Get additional analysis details"""
        pass

class HateSpeechAnalyzer(BaseContentAnalyzer):
    """Hate speech detection analyzer"""
    
    def __init__(self, model_path: str, vectorizer_path: str):
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)
    
    def predict(self, text: str) -> Tuple[str, float, str]:
        """Predict hate speech in text"""
        text_processed = text.lower()
        X = self.vectorizer.transform([text_processed])
        pred = self.model.predict(X)[0]
        proba = self.model.predict_proba(X)[0][1]  # Probability for class 1 (hate speech)
        
        # Determine prediction and confidence level
        if proba >= 0.7:
            prediction = "hate_speech"
            confidence = "high"
        elif proba >= 0.5:
            prediction = "hate_speech"
            confidence = "medium"
        elif proba >= 0.3:
            prediction = "likely_hate_speech"
            confidence = "low"
        else:
            prediction = "no_hate_speech"
            confidence = "high" if proba <= 0.1 else "medium"
        
        return prediction, proba, confidence
    
    def get_details(self) -> Dict[str, Any]:
        """Get hate speech analysis details"""
        return {
            "model_type": "hate_speech_classifier",
            "features_used": "text_vectorization",
            "threshold_info": {
                "hate_speech": ">= 0.5",
                "likely_hate_speech": "0.3-0.5",
                "no_hate_speech": "< 0.3"
            }
        }

class MisinformationAnalyzer(BaseContentAnalyzer):
    """Misinformation detection analyzer"""
    
    def __init__(self):
        # For now, this is a placeholder implementation
        # You can later add actual misinformation detection models
        pass
    
    def predict(self, text: str) -> Tuple[str, float, str]:
        """Predict misinformation in text"""
        # Placeholder implementation - replace with actual model
        # This is a simple keyword-based approach for demonstration
        
        misinformation_keywords = [
            'fake news', 'conspiracy', 'hoax', 'false claim', 
            'debunked', 'unverified', 'misleading'
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in misinformation_keywords if keyword in text_lower)
        
        # Simple probability based on keyword presence
        proba = min(keyword_count * 0.3, 0.9)
        
        if proba >= 0.6:
            prediction = "misinformation"
            confidence = "medium"
        elif proba >= 0.3:
            prediction = "likely_misinformation"
            confidence = "low"
        else:
            prediction = "no_misinformation"
            confidence = "low"  # Low confidence due to simple implementation
        
        return prediction, proba, confidence
    
    def get_details(self) -> Dict[str, Any]:
        """Get misinformation analysis details"""
        return {
            "model_type": "misinformation_classifier",
            "features_used": "keyword_detection",
            "note": "Placeholder implementation - replace with actual ML model",
            "threshold_info": {
                "misinformation": ">= 0.6",
                "likely_misinformation": "0.3-0.6",
                "no_misinformation": "< 0.3"
            }
        }

class ContentAnalyzerFactory:
    """Factory class to create appropriate content analyzers"""
    
    @staticmethod
    def create_hate_speech_analyzer(base_dir: str) -> HateSpeechAnalyzer:
        """Create hate speech analyzer with model files"""
        model_path = os.path.join(base_dir, "twitter_hate_model.joblib")
        vectorizer_path = os.path.join(base_dir, "twitter_hate_vectorizer.joblib")
        return HateSpeechAnalyzer(model_path, vectorizer_path)
    
    @staticmethod
    def create_misinformation_analyzer() -> MisinformationAnalyzer:
        """Create misinformation analyzer"""
        return MisinformationAnalyzer()