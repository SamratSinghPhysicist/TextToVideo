import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import requests
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
import time
from google import genai

GEMINI_API_KEY = "AIzaSyA0RYI9KRrNLi6KaX4g49UJD4G5YBEb6II"


class YouTubeShortsTopicGenerator:
    def __init__(self, client_secrets_file=None):
        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.client_secrets_file = client_secrets_file or "client_secrets.json"
        self.scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        self.youtube = None
        self.channel_id = None
        self.channel_data = {}
        self.videos_data = []
        self.analytics_data = {}
        self.trending_topics = []
        
        # Initialize NLTK resources
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
            
        # Add punkt_tab download
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab', quiet=True)
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        credentials = None
        
        # Check if token.pickle exists with stored credentials
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                credentials = pickle.load(token)
        
        # If credentials don't exist or are invalid, get new ones
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.scopes)
                credentials = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open('token.pickle', 'wb') as token:
                pickle.dump(credentials, token)
        
        # Build the YouTube API client
        self.youtube = build(self.api_service_name, self.api_version, credentials=credentials)
        print("Authentication successful!")
        return True
    
    def get_channel_info(self, channel_id=None):
        """Get basic information about the channel"""
        if channel_id:
            self.channel_id = channel_id
        else:
            # Get the authenticated user's channel
            request = self.youtube.channels().list(
                part="snippet,contentDetails,statistics",
                mine=True
            )
            response = request.execute()
            
            if not response['items']:
                print("No channel found for the authenticated user.")
                return False
            
            self.channel_id = response['items'][0]['id']
        
        # Get channel details
        request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics,brandingSettings",
            id=self.channel_id
        )
        response = request.execute()
        
        if not response['items']:
            print(f"No channel found with ID: {self.channel_id}")
            return False
        
        channel = response['items'][0]
        self.channel_data = {
            'id': channel['id'],
            'title': channel['snippet']['title'],
            'description': channel['snippet']['description'],
            'publishedAt': channel['snippet']['publishedAt'],
            'viewCount': int(channel['statistics'].get('viewCount', 0)),
            'subscriberCount': int(channel['statistics'].get('subscriberCount', 0)),
            'videoCount': int(channel['statistics'].get('videoCount', 0)),
            'keywords': channel.get('brandingSettings', {}).get('channel', {}).get('keywords', ''),
            'topic_categories': channel.get('topicDetails', {}).get('topicCategories', [])
        }
        
        print(f"Channel information retrieved for: {self.channel_data['title']}")
        return True
    
    def get_channel_videos(self, max_results=50, only_shorts=True):
        """Get videos from the channel, optionally filtering for shorts"""
        if not self.channel_id:
            print("Channel ID not set. Please run get_channel_info first.")
            return False
        
        # Get uploads playlist ID
        request = self.youtube.channels().list(
            part="contentDetails",
            id=self.channel_id
        )
        response = request.execute()
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get videos from uploads playlist
        videos = []
        next_page_token = None
        
        while True:
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=50,  # API maximum
                pageToken=next_page_token
            )
            response = request.execute()
            
            # Extract video IDs
            video_ids = [item['contentDetails']['videoId'] for item in response['items']]
            
            # Get detailed video information
            video_request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=','.join(video_ids)
            )
            video_response = video_request.execute()
            
            for video in video_response['items']:
                # Check if it's a short (vertical video with duration < 60 seconds)
                duration = self._parse_duration(video['contentDetails']['duration'])
                is_short = duration <= 60
                
                # Skip if we only want shorts and this isn't one
                if only_shorts and not is_short:
                    continue
                
                video_data = {
                    'id': video['id'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'publishedAt': video['snippet']['publishedAt'],
                    'tags': video['snippet'].get('tags', []),
                    'duration': duration,
                    'viewCount': int(video['statistics'].get('viewCount', 0)),
                    'likeCount': int(video['statistics'].get('likeCount', 0)),
                    'commentCount': int(video['statistics'].get('commentCount', 0)),
                    'is_short': is_short
                }
                
                videos.append(video_data)
                
                if len(videos) >= max_results:
                    break
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token or len(videos) >= max_results:
                break
        
        self.videos_data = videos
        print(f"Retrieved {len(videos)} videos from the channel.")
        return True
    
    def _parse_duration(self, duration_str):
        """Parse ISO 8601 duration format to seconds"""
        match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration_str)
        if not match:
            return 0
        
        hours = int(match.group(1)[:-1]) if match.group(1) else 0
        minutes = int(match.group(2)[:-1]) if match.group(2) else 0
        seconds = int(match.group(3)[:-1]) if match.group(3) else 0
        
        return hours * 3600 + minutes * 60 + seconds
    
    def analyze_channel_content(self):
        """Analyze the channel's content to identify patterns and successful topics"""
        if not self.videos_data:
            print("No video data available. Please run get_channel_videos first.")
            return False
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(self.videos_data)
        
        # Sort by view count to identify most successful videos
        df_sorted = df.sort_values('viewCount', ascending=False)
        
        # Calculate engagement rate (likes + comments) / views
        df['engagement_rate'] = (df['likeCount'] + df['commentCount']) / df['viewCount'].apply(lambda x: max(x, 1))
        
        # Extract topics from titles and descriptions
        all_text = ' '.join(df['title'] + ' ' + df['description'])
        topics = self._extract_topics(all_text)
        
        # Find correlation between topics and performance
        topic_performance = {}
        for topic in topics:
            # Find videos containing this topic
            topic_videos = df[df['title'].str.contains(topic, case=False) | 
                             df['description'].str.contains(topic, case=False)]
            
            if not topic_videos.empty:
                avg_views = topic_videos['viewCount'].mean()
                avg_engagement = topic_videos['engagement_rate'].mean()
                topic_performance[topic] = {
                    'avg_views': avg_views,
                    'avg_engagement': avg_engagement,
                    'video_count': len(topic_videos)
                }
        
        # Sort topics by performance
        sorted_topics = sorted(topic_performance.items(), 
                              key=lambda x: (x[1]['avg_views'], x[1]['avg_engagement']), 
                              reverse=True)
        
        self.analytics_data = {
            'top_performing_videos': df_sorted.head(10).to_dict('records'),
            'topic_performance': dict(sorted_topics),
            'channel_topics': topics,
            'avg_views': df['viewCount'].mean(),
            'avg_engagement': df['engagement_rate'].mean()
        }
        
        print("Channel content analysis complete.")
        return True
    
    def _extract_topics(self, text):
        """Extract meaningful topics from text"""
        # Tokenize and clean text
        try:
            tokens = word_tokenize(text.lower())
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                     if token.isalpha() and token not in self.stop_words and len(token) > 3]
            
            # Count word frequencies
            word_freq = Counter(tokens)
            
            # Extract bigrams (two-word phrases)
            bigrams = [' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)]
            bigram_freq = Counter(bigrams)
            
            # Combine single words and bigrams, prioritizing more frequent terms
            topics = [word for word, count in word_freq.most_common(30)]
            topics.extend([bigram for bigram, count in bigram_freq.most_common(20) 
                         if count > 2])  # Only include bigrams that appear multiple times
            
            return topics
        except LookupError as e:
            print(f"Error in topic extraction: {e}")
            print("Attempting to download missing NLTK resources...")
            nltk.download('punkt')
            nltk.download('punkt_tab')
            # Try again after downloading
            tokens = word_tokenize(text.lower())
            tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                     if token.isalpha() and token not in self.stop_words and len(token) > 3]
            
            # Count word frequencies
            word_freq = Counter(tokens)
            
            # Extract bigrams (two-word phrases)
            bigrams = [' '.join(tokens[i:i+2]) for i in range(len(tokens)-1)]
            bigram_freq = Counter(bigrams)
            
            # Combine single words and bigrams, prioritizing more frequent terms
            topics = [word for word, count in word_freq.most_common(30)]
            topics.extend([bigram for bigram, count in bigram_freq.most_common(20) 
                         if count > 2])  # Only include bigrams that appear multiple times
            
            return topics
    
    def get_trending_topics(self):
        """Get trending topics on YouTube"""
        # This is a simplified approach - in a real app, you might use:
        # 1. YouTube Trending videos API
        # 2. Google Trends API
        # 3. Third-party trend analysis services
        
        # For this example, we'll get trending videos and extract topics
        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                chart="mostPopular",
                regionCode="IN",  # Change to your target region
                videoCategoryId="0",  # General category
                maxResults=50
            )
            response = request.execute()
            
            trending_text = ' '.join([video['snippet']['title'] + ' ' + 
                                    video['snippet']['description'] 
                                    for video in response['items']])
            
            self.trending_topics = self._extract_topics(trending_text)
            print(f"Retrieved {len(self.trending_topics)} trending topics.")
            return True
            
        except googleapiclient.errors.HttpError as e:
            print(f"Error getting trending topics: {e}")
            # Fallback to some general trending topics
            self.trending_topics = ["challenge", "reaction", "tutorial", "review", 
                                  "day in life", "behind scenes", "how to", "tips tricks"]
            return False
    
    def generate_topic_suggestions(self, num_suggestions=10):
        """Generate topic suggestions based on channel analysis and trends"""
        if not self.analytics_data or not self.trending_topics:
            print("Missing analytics data or trending topics. Please run analyze_channel_content and get_trending_topics first.")
            return []
        
        suggestions = []
        
        # 1. Identify successful topics from your channel
        channel_topics = list(self.analytics_data['topic_performance'].keys())[:10]
        
        # 2. Find overlap with trending topics (these are high priority)
        overlapping_topics = [topic for topic in channel_topics 
                            if any(trend in topic or topic in trend 
                                  for trend in self.trending_topics)]
        
        # 3. Generate specific topic ideas
        for topic in overlapping_topics + channel_topics + self.trending_topics:
            if len(suggestions) >= num_suggestions:
                break
                
            # Create variations of the topic
            variations = [
                f"How to {topic}",
                f"{topic} challenge",
                f"Best {topic} tips",
                f"Why {topic} is trending",
                f"{topic} explained in 60 seconds",
                f"What you didn't know about {topic}"
            ]
            
            for variation in variations:
                if variation not in suggestions and len(suggestions) < num_suggestions:
                    suggestions.append(variation)
        
        # Ensure we have enough suggestions
        if len(suggestions) < num_suggestions:
            # Add some generic but effective formats
            formats = [
                "Day in the life of a {}",
                "3 things you didn't know about {}",
                "How I learned {} in one week",
                "The truth about {}",
                "I tried {} for a week",
                "Why everyone is talking about {}"
            ]
            
            # Add generic suggestions with channel topics
            for fmt in formats:
                for topic in channel_topics[:3]:  # Use top 3 channel topics
                    suggestion = fmt.format(topic)
                    if suggestion not in suggestions and len(suggestions) < num_suggestions:
                        suggestions.append(suggestion)
        
        return suggestions

    def print_topic_suggestions(self, suggestions):
        """Print topic suggestions in a formatted way"""
        print("\n" + "=" * 50)
        print("RECOMMENDED YOUTUBE SHORTS TOPICS FOR YOUR CHANNEL")
        print("=" * 50)
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
        
        print("\nThese suggestions are based on:")
        print(f"- Analysis of {len(self.videos_data)} videos from your channel")
        print(f"- {len(self.trending_topics)} current trending topics on YouTube")
        print(f"- Your channel's average view count: {int(self.analytics_data['avg_views'])}")
        print(f"- Your channel's average engagement rate: {self.analytics_data['avg_engagement']:.2%}")
        print("=" * 50)


def generate_gemini(prompt, api_key_gemini):
    client = genai.Client(api_key=api_key_gemini)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents= prompt,
    )
    # title = response.text
    print(response.text)
    return response.text

def title_generator_gemini(topic, api_key_gemini):
    is_script_generated = False
    try:
        prompt = f"""
        Generate one shorts video title for a YouTube Shorts video. The title should be written in Hinglish (a mix of Hindi and English). It should be concise, engaging, and ready for direct use in a text-to-video application.
        Do not say any other thing except the title itself as I will directly use the response given by (through code) without manually extracting the title. Also, generate only one title and not more. You can use emojis if needed. Also, include relevant video tags in the title like #facts #space , etc. Make sure that it is very shorts (not more than 50 words long) Please follow the example below:
        Few relevant video topics are: {topic}.
        Correct format (desired output) - Example of correct output:
        "Mars pe dragons mile 🥶🤯! #mars #fact #space"
        """
        title = generate_gemini(prompt, api_key_gemini)
        return title
    except Exception as e:
        # print("Error in generating script: ", e)
        is_script_generated = False
        return [f"Failed to generate title using gemini. Error \n: {e}", is_script_generated]


def main_topic_generator(GEMINI_API_KEY):
    # Instructions for getting client_secrets.json
    print("\nYouTube Shorts Topic Generator")
    print("=" * 30)
    print("\nBefore using this tool, you need to:")
    print("1. Create a project in Google Cloud Console")
    print("2. Enable the YouTube Data API v3")
    print("3. Create OAuth 2.0 credentials")
    print("4. Download the client_secrets.json file")
    print("\nFor detailed instructions, visit: https://developers.google.com/youtube/v3/getting-started")
    
    # Get client secrets file path
    client_secrets_file = "client_secrets.json"
    
    # Initialize the generator
    generator = YouTubeShortsTopicGenerator(client_secrets_file)
    
    # Authenticate with YouTube API
    if not generator.authenticate():
        print("Authentication failed. Please check your client_secrets.json file.")
        return
    
    # Get channel info
    # channel_id = input("\nEnter your YouTube channel ID (or press Enter to use authenticated user's channel): ")
    channel_id = None #I want to use the channel of authenticated user that is the channel who's token.pickle is available
    if not generator.get_channel_info(channel_id if channel_id else None):
        print("Failed to get channel information.")
        return
    
    # Get channel videos
    # max_results = int(input("\nHow many videos to analyze (max 50, default 30): ") or "30")
    max_results = 30
    #only_shorts = input("Analyze only Shorts? (y/n, default y): ").lower() != 'n'
    only_shorts = "y"
    if not generator.get_channel_videos(max_results, only_shorts):
        print("Failed to get channel videos.")
        return
    
    # Analyze channel content
    print("\nAnalyzing channel content...")
    if not generator.analyze_channel_content():
        print("Failed to analyze channel content.")
        return
    
    # Get trending topics
    print("\nFetching trending topics...")
    generator.get_trending_topics()  # Continue even if this fails (it has fallbacks)
    
    # Generate topic suggestions
    # num_suggestions = int(input("\nHow many topic suggestions do you want? (default 15): ") or "15")
    num_suggestions = 15
    suggestions = generator.generate_topic_suggestions(num_suggestions)
    
    # Print suggestions
    generator.print_topic_suggestions(suggestions)

    # Final best Title suggestion
    title = title_generator_gemini(suggestions, GEMINI_API_KEY)
    print("=" * 50)
    print("=" * 50)
    print(f"The Best title for your next youtube shorts video is:\n {title}")
    print("=" * 50)
    print("=" * 50)

    return title

"""
if __name__ == "__main__":
    main_topic_generator(GEMINI_API_KEY)
"""
