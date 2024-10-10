from django.shortcuts import render
from django.http import JsonResponse
from .models import ContentRequest
from .utils import generate_content
import json
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

logger = logging.getLogger(__name__)

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
            
            logger.info(f"Generating content for request: {content_request}")
            generated_content = await generate_content(content_request)
            
            # Check for any errors in the generated content
            errors = [platform for platform, result in generated_content.items() if result['content'].startswith('Error')]
            
            if errors:
                error_message = f"Errors occurred for platforms: {', '.join(errors)}. Content generation failed for these platforms."
                logger.error(error_message)
                # Instead of returning an error, we'll return partial results
                return JsonResponse({'content': generated_content, 'partial_error': error_message})
            
            logger.info("Content generated successfully for all platforms")
            return JsonResponse({'content': generated_content})
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
        except KeyError as e:
            logger.error(f"Missing key in request data: {str(e)}")
            return JsonResponse({'error': f'Missing required field: {str(e)}'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in generate view: {str(e)}", exc_info=True)
            return JsonResponse({'error': f"An unexpected error occurred: {str(e)}"}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)