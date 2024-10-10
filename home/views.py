from django.shortcuts import render
from django.http import JsonResponse
from .models import ContentRequest
from .utils import generate_content
import json
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

def index(request):
    return render(request,'index.html')

def home(request):
    return render(request, 'home.html')


def camel_to_snake(data):
    return {
        'category': data.get('category'),
        'description': data.get('description'),
        'platforms': data.get('platforms'),
        'word_count': data.get('wordCount'),  # Convert camelCase to snake_case
        'writing_style': data.get('writingStyle')  # Convert camelCase to snake_case
    }

@csrf_exempt
def generate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            converted_data = camel_to_snake(data)
            content_request = ContentRequest(**converted_data)
            generated_content = async_to_sync(generate_content)(content_request)
            
            if 'error' in generated_content:
                logger.error(f"Error in generate view: {generated_content['error']}")
                return JsonResponse({'error': 'An error occurred while generating content. Please try again.'}, status=500)
            
            return JsonResponse(generated_content)
        except Exception as e:
            logger.exception(f"Unexpected error in generate view: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred. Please try again.'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)