from django.shortcuts import render
from django.http import JsonResponse
from .models import ContentRequest
from .utils import generate_content
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import asyncio
import uuid
import logging

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')

@csrf_exempt
async def generate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"Received generate request with data: {data}")
            
            content_request = ContentRequest(
                category=data['category'],
                description=data['description'],
                platforms=data['platforms'],
                word_count=data['wordCount'],
                writing_style=data['writingStyle']
            )
            
            task_id = str(uuid.uuid4())
            cache.set(f"task_{task_id}_status", "PENDING", timeout=3600)
            logger.info(f"Created task with ID: {task_id}")
            
            # Start the content generation in the background
            asyncio.create_task(process_content_generation(task_id, content_request))
            
            return JsonResponse({'task_id': task_id})
        except Exception as e:
            logger.error(f"Error in generate view: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

async def process_content_generation(task_id, content_request):
    try:
        logger.info(f"Starting content generation for task {task_id}")
        generated_content = await generate_content(content_request)
        logger.info(f"Content generation complete for task {task_id}")
        cache.set(f"task_{task_id}_result", generated_content, timeout=3600)
        cache.set(f"task_{task_id}_status", "COMPLETE", timeout=3600)
    except Exception as e:
        logger.error(f"Error in content generation for task {task_id}: {str(e)}")
        cache.set(f"task_{task_id}_status", "ERROR", timeout=3600)
        cache.set(f"task_{task_id}_error", str(e), timeout=3600)

@csrf_exempt
def check_task_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')
            logger.info(f"Checking status for task {task_id}")
            
            status = cache.get(f"task_{task_id}_status")
            logger.info(f"Status for task {task_id}: {status}")
            
            if status == "COMPLETE":
                result = cache.get(f"task_{task_id}_result")
                return JsonResponse({'status': 'COMPLETE', 'result': result})
            elif status == "ERROR":
                error = cache.get(f"task_{task_id}_error")
                return JsonResponse({'status': 'ERROR', 'error': error})
            else:
                return JsonResponse({'status': 'PENDING'})
        except Exception as e:
            logger.error(f"Error in check_task_status view: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)