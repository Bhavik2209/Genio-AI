import google.generativeai as genai
from django.conf import settings
import asyncio
from asgiref.sync import sync_to_async
from collections import deque

genai.configure(api_key=settings.GEMINI_API_KEY)

async def generate_content_for_platform(model, content_request, platform):
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


    try:
        response = await sync_to_async(model.generate_content)(prompt)
        return platform, response.text
    except Exception as e:
        return platform, f"Error generating content: {str(e)}"

async def process_platform_queue(model, queue, content_request, results):
    while queue:
        platform = queue.popleft()
        platform, content = await generate_content_for_platform(model, content_request, platform)
        results[platform] = content

async def generate_content(content_request):
    models = [
        genai.GenerativeModel('gemini-pro'),
        genai.GenerativeModel('gemini-pro'),
        genai.GenerativeModel('gemini-pro')
    ]
    
    platforms = content_request.platforms.split(',')
    platform_queue = deque(platforms)
    results = {}
    
    tasks = [
        process_platform_queue(model, platform_queue, content_request, results)
        for model in models
    ]
    
    await asyncio.gather(*tasks)
    
    return results