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
        try:
            data = json.loads(request.body)
            
            content_request = ContentRequest(
                category=data['category'],
                description=data['description'],
                platforms=data['platforms'],
                word_count=data['wordCount'],
                writing_style=data['writingStyle']
            )
            
            generated_content = await generate_content(content_request)
            
            # Check for any errors in the generated content
            errors = [platform for platform, result in generated_content.items() if result['content'].startswith('Error')]
            
            if errors:
                error_message = f"Errors occurred for platforms: {', '.join(errors)}. Please try again or reduce the number of platforms/word count."
                return JsonResponse({'error': error_message}, status=500)
            
            return JsonResponse({'content': generated_content})
        except Exception as e:
            return JsonResponse({'error': f"An unexpected error occurred: {str(e)}"}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)