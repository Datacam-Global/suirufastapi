import os
import requests
from typing import Tuple, Any, Dict

class MisinformationAnalyzer:
    """Misinformation detection analyzer with OpenAI support"""
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def predict(self, text: str) -> Tuple[str, float, str]:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a fact-checking assistant."},
                        {"role": "user", "content": f"Fact check the following claim. Claim: {text} Is the claim true, false, or unverifiable? Respond with one word: true, false, or unverifiable."}
                    ],
                    "max_tokens": 5,
                    "temperature": 0
                }
                url = "https://api.openai.com/v1/chat/completions"
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
            "features_used": "openai",
            "note": "Uses OpenAI for misinformation detection",
            "threshold_info": {
                "misinformation": ">= 0.6",
                "likely_misinformation": "0.3-0.6",
                "no_misinformation": "< 0.3"
            }
        }
