import joblib
import os
from typing import Tuple, Dict, Any
from abc import ABC, abstractmethod
import requests
import openai
import sys

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
    """Misinformation detection analyzer with Azure OpenAI support"""
    
    def __init__(self, api_key: str = None):
        # Use API key from env if not provided
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")

    def predict(self, text: str) -> Tuple[str, float, str]:
        # Print env config for debugging
        print(f"[Azure OpenAI Config] API_KEY={os.getenv('AZURE_OPENAI_API_KEY')}", file=sys.stderr)
        print(f"[Azure OpenAI Config] ENDPOINT={os.getenv('AZURE_OPENAI_ENDPOINT')}", file=sys.stderr)
        print(f"[Azure OpenAI Config] DEPLOYMENT={os.getenv('AZURE_OPENAI_DEPLOYMENT')}", file=sys.stderr)
        print(f"[Azure OpenAI Config] API_VERSION={os.getenv('AZURE_OPENAI_API_VERSION')}", file=sys.stderr)
        # Use only Azure OpenAI for misinformation detection
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        if azure_api_key and azure_endpoint and azure_deployment and azure_api_version:
            try:
                headers = {
                    "api-key": azure_api_key,
                    "Content-Type": "application/json"
                }
                data = {
                    "messages": [
                        {"role": "system", "content": "You are a fact-checking assistant."},
                        {"role": "user", "content": f"Fact check the following claim. Claim: {text} Is the claim true, false, or unverifiable? Respond with one word: true, false, or unverifiable."}
                    ],
                    "max_tokens": 5,
                    "temperature": 0
                }
                url = f"{azure_endpoint}openai/deployments/{azure_deployment}/chat/completions?api-version={azure_api_version}"
                response = requests.post(url, headers=headers, json=data, timeout=20)
                print(f"[Azure OpenAI Request] url={url} data={data}", file=sys.stderr)
                print(f"[Azure OpenAI Response] status={response.status_code} body={response.text}", file=sys.stderr)
                if response.status_code == 200:
                    result = response.json()
                    answer = result["choices"][0]["message"]["content"].strip().lower()
                    if answer == "false":
                        return "misinformation", 0.7, "medium"
                    elif answer == "unverifiable":
                        return "unverified", 0.0, "unknown"
                    else:
                        return "no_misinformation", 0.0, "low"
            except Exception as e:
                print(f"[Azure OpenAI Exception] {e}", file=sys.stderr)
                return "unverified", 0.0, "unknown"
        # If Azure OpenAI config is missing or fails
        print("[Azure OpenAI] Missing configuration or failed to execute.", file=sys.stderr)
        return "unverified", 0.0, "unknown"

    def get_details(self) -> Dict[str, Any]:
        """Get misinformation analysis details"""
        return {
            "model_type": "misinformation_classifier",
            "features_used": "azure_openai",
            "note": "Uses Azure OpenAI for misinformation detection",
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
        """Create misinformation analyzer with Azure OpenAI support"""
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        return MisinformationAnalyzer(api_key=api_key)