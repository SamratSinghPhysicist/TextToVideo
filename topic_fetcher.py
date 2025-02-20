import random
from googleapiclient.discovery import build

from script_generator import generate_gemini



def get_youtube_shorts(api_key, query, max_results=random.randint(10, 50)):
    """
    Query the YouTube Data API for short videos based on a given query.
    Shorts are typically videos under 60 seconds. The 'videoDuration' parameter
    is used to filter for short videos.
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    search_response = youtube.search().list(
        q=query,
        type='video',
        videoDuration='short',  # Filter for videos under 4 minutes; adjust if needed.
        maxResults=max_results,
        part='id,snippet'
    ).execute()

    videos = []
    for item in search_response.get('items', []):
        video_data = {
            'video_id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description']
        }
        videos.append(video_data)
    return videos


def generate_topic_ideas(base_data, GEMINI_API_KEY):
    """
    Generate refined topic ideas.
    If Gemini-2.0-flash is available, use it to generate suggestions.
    Otherwise, fall back to a simple placeholder logic.
    """
    prompt = f"""Generate only one engaging YouTube Shorts topic based on these data: {base_data}. Keep it click-worthy and engaging. Also, just generate the title of the video and nothing else (Don't say anything like here is your title).

    Correct format (desired output) - Example of correct output:
    "Jupiter pe diamond ki baarish 😮🤑"
        
    Incorrect format (what to avoid) - Example of Incorrect output:
    "Here is the title of your youtube shorts:
    Jupiter pe diamond ki baarish 😮🤑"
    """
    generated_topic = generate_gemini(prompt, GEMINI_API_KEY)

    return generated_topic

def main_topic_generator(YOUTUBE_API_KEY, channel_niche, GEMINI_API_KEY):
    # YouTube API key and the base query for your channel's niche.

    # YOUTUBE_API_KEY = 'YOUR_YOUTUBE_API_KEY'
    # channel_query = "tech shorts"  # Modify this to suit your channel's niche.

    # 1. Retrieve YouTube Shorts relevant to your channel.
    youtube_shorts = get_youtube_shorts(YOUTUBE_API_KEY, channel_niche)
    print("YouTube Shorts based on query:")
    for video in youtube_shorts:
        print(f"- {video['title']} (ID: {video['video_id']})")


    # 3. Combine data from YouTube and trending keywords.
    base_data = []
    # Extract video titles from YouTube Shorts.
    for video in youtube_shorts:
        base_data.append(video['title'])

    # Remove duplicates while preserving order.
    seen = set()
    base_data = [x for x in base_data if not (x in seen or seen.add(x))]

    # 4. Generate topic ideas using the base data.
    generated_topic = generate_topic_ideas(base_data, GEMINI_API_KEY)
    print(f"Generated topic is: {generated_topic}")


"""
if __name__ == "__main__":
    main_topic_generator(YOUTUBE_API_KEY, "space facts", GEMINI_API_KEY)
"""
