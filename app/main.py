# Entrypoint for FastAPI app
from fastapi import FastAPI
from app.api import endpoints_hate, endpoints_misinfo
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Debug prints for Azure OpenAI environment variables
print("[DEBUG] AZURE_OPENAI_API_KEY:", os.getenv("AZURE_OPENAI_API_KEY"))
print("[DEBUG] AZURE_OPENAI_ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("[DEBUG] AZURE_OPENAI_DEPLOYMENT:", os.getenv("AZURE_OPENAI_DEPLOYMENT"))
print("[DEBUG] AZURE_OPENAI_API_VERSION:", os.getenv("AZURE_OPENAI_API_VERSION"))

# Use prefixes so both sets of endpoints are visible and do not conflict
app.include_router(endpoints_hate.router, prefix="/hate", tags=["Hate Speech"])
app.include_router(endpoints_misinfo.router, prefix="/misinformation", tags=["Misinformation"])

# Optionally, add a root endpoint or docs customization here
