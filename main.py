# Entrypoint for running the FastAPI app
# This file simply imports and runs the app from hate_speech_api.py

from hate_speech_api import app

# This allows: uvicorn main:app --reload
