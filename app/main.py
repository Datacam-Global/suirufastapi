# Entrypoint for FastAPI app
from fastapi import FastAPI
from app.api import endpoints_hate, endpoints_misinfo
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
import uvicorn

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

class TrailingSlashMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.endswith('/') and len(request.url.path) > 1:
            return RedirectResponse(url=str(request.url).rstrip('/'))
        return await call_next(request)

app.add_middleware(TrailingSlashMiddleware)

# CORS (Cross-Origin Resource Sharing) middleware
# This is important for allowing frontend applications to communicate with your API
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:3000",
    "https://server.sui-ru.com",
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
