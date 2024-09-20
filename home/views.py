from django.shortcuts import render
from django.http import JsonResponse
from .models import ContentRequest
from .utils import generate_content
import json
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from .utils import generate_content

# Global dictionary to store tasks
tasks = {}

@csrf_exempt
async def generate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        content_request = ContentRequest(
            category=data['category'],
            description=data['description'],
            platforms=','.join(data['platforms']),
            word_count=data['wordCount'],
            writing_style=data['writingStyle']
        )
        
        task_id = str(uuid.uuid4())
        tasks[task_id] = {'status': 'processing', 'result': None}
        
        # Start the task without awaiting its completion
        asyncio.create_task(process_content_generation(task_id, content_request))
        
        return JsonResponse({'task_id': task_id})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

async def process_content_generation(task_id, content_request):
    try:
        result = await generate_content(content_request)
        tasks[task_id] = {'status': 'completed', 'result': result}
    except Exception as e:
        tasks[task_id] = {'status': 'failed', 'error': str(e)}

@csrf_exempt
async def check_task_status(request, task_id):
    task = tasks.get(task_id)
    if task is None:
        return JsonResponse({'status': 'not_found'})
    if task['status'] == 'completed':
        result = task['result']
        del tasks[task_id]  # Clean up completed task
        return JsonResponse({'status': 'completed', 'result': result})
    if task['status'] == 'failed':
        error = task['error']
        del tasks[task_id]  # Clean up failed task
        return JsonResponse({'status': 'failed', 'error': error})
    return JsonResponse({'status': 'processing'})

def index(request):
    return render(request,'index.html')

def home(request):
    return render(request, 'home.html')

# @csrf_exempt
# async def generate(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
        
#         content_request = await sync_to_async(ContentRequest.objects.create)(
#             category=data['category'],
#             description=data['description'],
#             platforms=','.join(data['platforms']),
#             word_count=data['wordCount'],
#             writing_style=data['writingStyle']
#         )
        
#         generated_content = await generate_content(content_request)
        
#         return JsonResponse({'content': generated_content})
    
#     return JsonResponse({'error': 'Invalid request method'}, status=400)