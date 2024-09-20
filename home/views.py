from django.shortcuts import render
from django.http import JsonResponse
from .models import ContentRequest
from .utils import generate_content
import json
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')

@csrf_exempt
async def generate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Create a ContentRequest instance without saving to the database
        content_request = ContentRequest(
            category=data['category'],
            description=data['description'],
            platforms=','.join(data['platforms']),
            word_count=data['wordCount'],
            writing_style=data['writingStyle']
        )
        
        generated_content = await generate_content(content_request)
        
        return JsonResponse({'content': generated_content})
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)