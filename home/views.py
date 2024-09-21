from django.shortcuts import render
from django.http import JsonResponse
from .models import ContentRequest
from .utils import generate_content
import json
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

def index(request):
    return render(request,'index.html')

def home(request):
    return render(request, 'home.html')

@csrf_exempt
async def generate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        content_request = await sync_to_async(ContentRequest.objects.create)(
            category=data['category'],
            description=data['description'],
            platforms=','.join(data['platforms']),
            word_count=data['wordCount'],
            writing_style=data['writingStyle']
        )
        
        generated_content = await generate_content(content_request)
        
        return JsonResponse({'content': generated_content})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)