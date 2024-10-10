import aiohttp
from django.conf import settings
import asyncio
from collections import deque
import json
import logging
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HUGGINGFACE_API_KEY = settings.HUGGINGFACE_API_KEY

async def generate_content_for_platform(content_request, platform):
    prompt = f''' # Enhanced Content Generation Prompt

Create {platform}-specific content that aligns with the following parameters:

1. Style: {content_request.writing_style}, strictly follow this style
2. Word count: Approximately {content_request.word_count} words
3. Description: {content_request.description} keep this in attention

## General Guidelines:
- Craft engaging, insightful, and original content that resonates with the target audience
- Ensure the content is plagiarism-free and impactful
- Incorporate relevant emojis where suitable to enhance engagement
- Add a human touch to make the content relatable and authentic
- Make the content logical, engaging, and highly useful for the audience
- Adapt tone and language to suit the specified platform and audience demographics

## Platform-Specific Instructions:

### LinkedIn:
Create a post that includes:
- A compelling headline or opening statement
- Professional insights or industry-relevant information
- Calls for engagement (e.g., "What are your thoughts on this?")
- Relevant hashtags (3-5) to increase visibility
- A concise yet impactful structure suitable for LinkedIn's format

### Twitter:
Generate a series of tweets that:
- Fit within Twitter's character limit (280 characters per tweet)
- Use thread format for longer content, ensuring each tweet can stand alone
- Incorporate relevant hashtags and mentions where appropriate
- Include calls-to-action for retweets, likes, or responses
- Utilize Twitter-specific features like polls or quote tweets if relevant

### Reddit:
Develop a post that:
- Has a clear, attention-grabbing title
- Provides valuable information or sparks discussion
- Follows the specific rules and culture of the chosen subreddit
- Includes a TL;DR (Too Long; Didn't Read) summary for longer posts
- Encourages community engagement and comments

### Blog:
Create a blog post that:
- Has a compelling title and introduction
- Is well-structured with headings, subheadings, and paragraphs
- Includes relevant keywords for SEO without keyword stuffing
- Provides in-depth analysis or information on the topic
- Ends with a conclusion and call-to-action

### YouTube:
Generate a video script that includes:
- An attention-grabbing introduction
- Clear segmentation of main points or topics
- Engaging transitions between segments
- A strong call-to-action at the end
- Suggestions for visual elements or B-roll to accompany the script

### Product Hunt:
Craft a product launch post that:
- Has a concise, compelling tagline
- Clearly explains the product's unique value proposition
- Includes key features and benefits
- Provides pricing information (if applicable)
- Encourages upvotes and comments

### Peerlist:
Create a professional showcase post that:
- Highlights specific skills, achievements, or projects
- Uses a tone that balances professionalism and personality
- Includes relevant tags for discoverability
- Encourages connections and professional networking
- Showcases your expertise in a specific area

### Dev.to:
Write a technical post that:
- Has a clear, descriptive title
- Includes code snippets or examples where relevant
- Explains complex concepts in an accessible manner
- Uses appropriate tags for the Dev.to community
- Encourages discussion and knowledge sharing

### Hacker News:
Develop a submission that:
- Has a factual, non-sensationalized title
- Provides high-quality, intellectually interesting content
- Follows Hacker News guidelines and community norms
- Sparks meaningful discussion on technology or startups
- Avoids self-promotion unless it's truly noteworthy

Ensure the content is tailored to the unique characteristics and audience expectations of the specified platform while maintaining the requested style, word count, and alignment with the provided description.'''

    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_length": 1000, "min_length": 50}
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(HUGGINGFACE_API_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return platform, result[0]['generated_text'].strip()
                else:
                    error_message = f"Error: API returned status code {response.status}"
                    logger.error(f"Hugging Face API error: {error_message}")
                    return platform, error_message
        except Exception as e:
            error_message = f"Error generating content: {str(e)}"
            logger.exception(f"Exception in generate_content_for_platform: {error_message}")
            return platform, error_message

async def process_platform_queue(queue, content_request, results, semaphore):
    while queue:
        platform = queue.popleft()
        async with semaphore:
            try:
                platform, content = await generate_content_for_platform(content_request, platform)
                results[platform] = content
            except Exception as e:
                logger.exception(f"Exception in process_platform_queue for platform {platform}: {str(e)}")
                results[platform] = f"Error processing platform {platform}: {str(e)}"

async def generate_content(content_request):
    platform_queue = deque(content_request.platforms)
    results = {}
    
    # Limit concurrent requests
    semaphore = asyncio.Semaphore(5)  # Adjust this value based on your needs and API limits
    
    try:
        tasks = [process_platform_queue(platform_queue.copy(), content_request, results, semaphore)]
        # Add a timeout of 25 seconds (adjust as needed)
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=25)
    except asyncio.TimeoutError:
        logger.error("Content generation timed out")
        results['error'] = "Content generation timed out. Please try again or generate for fewer platforms."
    except Exception as e:
        logger.exception(f"Exception in generate_content: {str(e)}")
        results['error'] = f"An error occurred while generating content: {str(e)}"
    
    return results