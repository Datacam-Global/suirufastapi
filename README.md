# Cameroon Hate Speech Detection FastAPI Project

## Running the API

1. **Install dependencies** (recommended: use a virtual environment):
   ```bash
   pip install -r requirements_api.txt
   ```

2. **Start the FastAPI server**:
   ```bash
   uvicorn hate_speech_api:app --host 0.0.0.0 --port 8000 --reload
   ```
   - For production, remove `--reload` and consider using multiple workers:
     ```bash
     uvicorn hate_speech_api:app --host 0.0.0.0 --port 8000 --workers 4
     ```

3. **API Documentation**:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Project Structure
- `hate_speech_api.py`: Main FastAPI app and endpoints
- `hate_speech_detector.py`: Detection logic
- `realtime_monitor.py`: Database and monitoring
- `requirements_api.txt`: Python dependencies

## Example Usage
Test the API with curl:
```bash
curl -X POST "http://localhost:8000/analyze" -H "Content-Type: application/json" -d '{"text": "This is a test."}'
```
