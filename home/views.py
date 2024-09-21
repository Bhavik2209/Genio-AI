from django.shortcuts import render
from django.http import JsonResponse
from .models import ContentRequest
from .utils import generate_content
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import asyncio
import uuid

def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')

@csrf_exempt
async def generate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        content_request = ContentRequest(
            category=data['category'],
            description=data['description'],
            platforms=data['platforms'],
            word_count=data['wordCount'],
            writing_style=data['writingStyle']
        )
        
        task_id = str(uuid.uuid4())
        cache.set(f"task_{task_id}_status", "PENDING", timeout=3600)
        
        # Start the content generation in the background
        asyncio.create_task(process_content_generation(task_id, content_request))
        
        return JsonResponse({'task_id': task_id})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

async def process_content_generation(task_id, content_request):
    try:
        generated_content = await generate_content(content_request)
        cache.set(f"task_{task_id}_result", generated_content, timeout=3600)
        cache.set(f"task_{task_id}_status", "COMPLETE", timeout=3600)
    except Exception as e:
        cache.set(f"task_{task_id}_status", "ERROR", timeout=3600)
        cache.set(f"task_{task_id}_error", str(e), timeout=3600)

@csrf_exempt
def check_task_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_id = data.get('task_id')
        
        status = cache.get(f"task_{task_id}_status")
        if status == "COMPLETE":
            result = cache.get(f"task_{task_id}_result")
            return JsonResponse({'status': 'COMPLETE', 'result': result})
        elif status == "ERROR":
            error = cache.get(f"task_{task_id}_error")
            return JsonResponse({'status': 'ERROR', 'error': error})
        else:
            return JsonResponse({'status': 'PENDING'})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)