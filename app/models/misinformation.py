import os
import requests
from typing import Tuple, Any, Dict

class MisinformationAnalyzer:
    """Misinformation detection analyzer with Azure OpenAI support"""
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")

    def predict(self, text: str) -> Tuple[str, float, str]:
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
                return "unverified", 0.0, "unknown"
        return "unverified", 0.0, "unknown"

    def get_details(self) -> Dict[str, Any]:
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
