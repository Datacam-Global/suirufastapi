# Django Integration Guide

This guide shows how to integrate your Django application at `server.sui-ru.com` with the FastAPI Content Analysis service.

## API Endpoints

Once deployed, your FastAPI service will be available at: `http://your-azure-container-url:8000`

### Available Endpoints

1. **General Content Analysis** (Recommended)
   - **URL**: `POST /content/analyze`
   - **Purpose**: Analyze content for hate speech or misinformation

2. **Hate Speech Specific**
   - **URL**: `POST /hate-speech/analyze`
   - **Purpose**: Analyze text specifically for hate speech

3. **Misinformation Specific**
   - **URL**: `POST /misinformation/analyze`
   - **Purpose**: Analyze text for misinformation

4. **Legacy Endpoint**
   - **URL**: `POST /predict`
   - **Purpose**: Backward compatibility (deprecated)

5. **Health Check**
   - **URL**: `GET /health`
   - **Purpose**: Check if the service is running

## Django Integration Code

### 1. Create a Service Class

Create `services/content_analysis.py` in your Django app:

```python
import requests
import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class ContentAnalysisService:
    def __init__(self):
        # Configure this in your Django settings
        self.base_url = getattr(settings, 'CONTENT_ANALYSIS_API_URL', 'http://your-azure-container-url:8000')
        self.timeout = getattr(settings, 'CONTENT_ANALYSIS_TIMEOUT', 30)
        
    def analyze_content(self, text: str, content_type: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze content using the general content analysis endpoint
        
        Args:
            text: The text to analyze
            content_type: Either 'hate_speech' or 'misinformation'
            metadata: Optional metadata to include in the request
            
        Returns:
            Dictionary with analysis results
        """
        url = f"{self.base_url}/content/analyze"
        payload = {
            "text": text,
            "content_type": content_type
        }
        
        if metadata:
            payload["metadata"] = metadata
            
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Content analysis API error: {e}")
            raise ContentAnalysisException(f"API request failed: {e}")
    
    def analyze_hate_speech(self, text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze text specifically for hate speech
        """
        url = f"{self.base_url}/hate-speech/analyze"
        payload = {"text": text}
        
        if metadata:
            payload["metadata"] = metadata
            
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Hate speech analysis API error: {e}")
            raise ContentAnalysisException(f"API request failed: {e}")
    
    def analyze_misinformation(self, text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze text for misinformation
        """
        url = f"{self.base_url}/misinformation/analyze"
        payload = {"text": text}
        
        if metadata:
            payload["metadata"] = metadata
            
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Misinformation analysis API error: {e}")
            raise ContentAnalysisException(f"API request failed: {e}")
    
    def check_health(self) -> bool:
        """
        Check if the content analysis service is healthy
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def legacy_predict(self, text: str) -> Dict[str, Any]:
        """
        Legacy endpoint for backward compatibility
        """
        url = f"{self.base_url}/predict"
        payload = {"text": text}
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Legacy prediction API error: {e}")
            raise ContentAnalysisException(f"API request failed: {e}")

class ContentAnalysisException(Exception):
    """Custom exception for content analysis errors"""
    pass
```

### 2. Django Settings Configuration

Add to your `settings.py`:

```python
# Content Analysis API Configuration
CONTENT_ANALYSIS_API_URL = 'http://your-azure-container-url:8000'  # Update after deployment
CONTENT_ANALYSIS_TIMEOUT = 30  # seconds

# Add to INSTALLED_APPS if creating a new app
INSTALLED_APPS = [
    # ... your existing apps
    'content_analysis',  # if you create a separate app
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'content_analysis.log',
        },
    },
    'loggers': {
        'services.content_analysis': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### 3. Usage Examples

#### In Django Views

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from services.content_analysis import ContentAnalysisService, ContentAnalysisException
import json

@method_decorator(csrf_exempt, name='dispatch')
class ContentAnalysisView(View):
    def __init__(self):
        super().__init__()
        self.content_service = ContentAnalysisService()
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            content_type = data.get('content_type', 'hate_speech')
            
            if not text:
                return JsonResponse({'error': 'Text is required'}, status=400)
            
            # Analyze content
            result = self.content_service.analyze_content(
                text=text,
                content_type=content_type,
                metadata={
                    'user_id': request.user.id if request.user.is_authenticated else None,
                    'timestamp': str(timezone.now()),
                    'source': 'django_app'
                }
            )
            
            return JsonResponse(result)
            
        except ContentAnalysisException as e:
            return JsonResponse({'error': str(e)}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Internal server error'}, status=500)

# Alternative: Function-based view
@csrf_exempt
def analyze_text(request):
    if request.method == 'POST':
        service = ContentAnalysisService()
        
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            
            # Use specific endpoint
            result = service.analyze_hate_speech(text)
            
            return JsonResponse(result)
            
        except ContentAnalysisException as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
```

#### In Django Models (Celery Task)

```python
from celery import shared_task
from services.content_analysis import ContentAnalysisService
from .models import Post

@shared_task
def analyze_post_content(post_id):
    """
    Async task to analyze post content
    """
    try:
        post = Post.objects.get(id=post_id)
        service = ContentAnalysisService()
        
        # Analyze for hate speech
        hate_result = service.analyze_hate_speech(
            text=post.content,
            metadata={'post_id': post_id, 'user_id': post.user_id}
        )
        
        # Update post with analysis results
        post.hate_speech_probability = hate_result['probability']
        post.hate_speech_prediction = hate_result['prediction']
        post.save()
        
        return f"Analyzed post {post_id}: {hate_result['prediction']}"
        
    except Exception as e:
        return f"Error analyzing post {post_id}: {str(e)}"
```

### 4. URL Configuration

Add to your `urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('api/analyze/', views.ContentAnalysisView.as_view(), name='analyze_content'),
    path('api/analyze-text/', views.analyze_text, name='analyze_text'),
]
```

## API Response Examples

### General Content Analysis Response
```json
{
    "content_type": "hate_speech",
    "prediction": "hate_speech",
    "probability": 0.85,
    "confidence_level": "high",
    "analysis_details": {
        "model_version": "1.0",
        "processing_time": 0.045,
        "request_metadata": {
            "user_id": 123,
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }
}
```

### Hate Speech Analysis Response
```json
{
    "prediction": "hate_speech",
    "probability": 0.92,
    "confidence_level": "high",
    "details": {
        "model_type": "hate_speech_classifier",
        "processing_time": 0.032
    }
}
```

### Error Response
```json
{
    "error": "ValidationError",
    "message": "Text field is required",
    "details": {
        "field": "text",
        "code": "required"
    }
}
```

## Testing

### 1. Unit Tests

```python
import unittest
from unittest.mock import patch, Mock
from services.content_analysis import ContentAnalysisService, ContentAnalysisException

class TestContentAnalysisService(unittest.TestCase):
    def setUp(self):
        self.service = ContentAnalysisService()
    
    @patch('requests.post')
    def test_analyze_content_success(self, mock_post):
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            'content_type': 'hate_speech',
            'prediction': 'no_hate_speech',
            'probability': 0.15,
            'confidence_level': 'high'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.service.analyze_content('Hello world', 'hate_speech')
        
        self.assertEqual(result['prediction'], 'no_hate_speech')
        self.assertEqual(result['probability'], 0.15)
    
    @patch('requests.post')
    def test_analyze_content_failure(self, mock_post):
        # Mock failed response
        mock_post.side_effect = requests.exceptions.RequestException("API Error")
        
        with self.assertRaises(ContentAnalysisException):
            self.service.analyze_content('Hello world', 'hate_speech')
```

### 2. Integration Tests

```python
from django.test import TestCase
from services.content_analysis import ContentAnalysisService

class ContentAnalysisIntegrationTest(TestCase):
    def setUp(self):
        self.service = ContentAnalysisService()
    
    def test_health_check(self):
        """Test if the API is accessible"""
        is_healthy = self.service.check_health()
        self.assertTrue(is_healthy, "Content analysis API should be healthy")
    
    def test_analyze_sample_text(self):
        """Test analyzing a sample text"""
        result = self.service.analyze_hate_speech("This is a test message")
        
        self.assertIn('prediction', result)
        self.assertIn('probability', result)
        self.assertIsInstance(result['probability'], float)
```

## Deployment Checklist

1. ✅ **Deploy FastAPI to Azure Container Instances**
2. ✅ **Update Django settings** with the correct API URL
3. ✅ **Configure CORS** in FastAPI to allow requests from server.sui-ru.com
4. ✅ **Test API connectivity** from Django app
5. ✅ **Set up monitoring** and logging
6. ✅ **Configure error handling** for API failures
7. ✅ **Set up health checks** in Django

## Monitoring and Logging

### Django Logging Setup

```python
# Add to Django settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'content_analysis_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/content_analysis.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'services.content_analysis': {
            'handlers': ['content_analysis_file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Health Check Endpoint

```python
# Add to Django views
def api_health_check(request):
    """Check if external APIs are healthy"""
    service = ContentAnalysisService()
    
    health_status = {
        'content_analysis_api': service.check_health(),
        'timestamp': timezone.now().isoformat()
    }
    
    status_code = 200 if health_status['content_analysis_api'] else 503
    return JsonResponse(health_status, status=status_code)
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure server.sui-ru.com is in the CORS allowed origins
2. **Timeout Errors**: Increase the timeout setting in Django
3. **Connection Refused**: Check if the FastAPI service is running and accessible
4. **Model Loading Errors**: Check Azure Container Instance logs

### Debug Commands

```bash
# Check if API is accessible from Django server
curl -X POST http://your-azure-container-url:8000/health

# Test content analysis endpoint
curl -X POST http://your-azure-container-url:8000/content/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "test message", "content_type": "hate_speech"}'
```
