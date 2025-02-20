import os
import schedule
import time
import pickle
import random

from dotenv import load_dotenv
from script_generator import script_generator
from voiceover_generator import text_to_speech
from image_generator import main_image_function
from video_generator import generate_final_video
from topic_fetcher import main_topic_generator

# Load API keys from .env file
load_dotenv()

# API keys for account_1=samratddypppis@gmail.com
GEMINI_API_KEY_1 = os.getenv("GEMINI_API_KEY_1")
ELEVENLABS_API_KEY_1 = os.getenv("ELEVENLABS_API_KEY_1")
VOICE_ID_1 = os.getenv("VOICE_ID_1")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# API keys for account_2=samrat1212study2@gmail.com
GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")
ELEVENLABS_API_KEY_2 = os.getenv("ELEVENLABS_API_KEY_2")
VOICE_ID_2 = os.getenv("VOICE_ID_2")

# API keys for account_3=sam1212factz@gmail.com
GEMINI_API_KEY_3 = os.getenv("GEMINI_API_KEY_3")
ELEVENLABS_API_KEY_3 = os.getenv("ELEVENLABS_API_KEY_3")
VOICE_ID_3 = os.getenv("VOICE_ID_3")

IMAGEPIG_API_KEY = os.getenv("IMAGEPIG_API_KEY")

# API keys for account_4=samrat1212study@gmail.com
GEMINI_API_KEY_4 = "NOT MADE YET"
ELEVENLABS_API_KEY_4 = os.getenv("ELEVENLABS_API_KEY_4")
VOICE_ID_4 = os.getenv("VOICE_ID_4")

# API Keys for different accounts
api_key = {
    'account_1': [GEMINI_API_KEY_1, ELEVENLABS_API_KEY_1, VOICE_ID_1, IMAGEPIG_API_KEY],
    'account_2': [GEMINI_API_KEY_2, ELEVENLABS_API_KEY_2, VOICE_ID_2, IMAGEPIG_API_KEY],
    'account_3': [GEMINI_API_KEY_3, ELEVENLABS_API_KEY_3, VOICE_ID_3, IMAGEPIG_API_KEY],
    'account_4': [GEMINI_API_KEY_4, ELEVENLABS_API_KEY_4, VOICE_ID_4, IMAGEPIG_API_KEY]
}

# ---------------------------
# Existing video generation functions
# ---------------------------
def script_receiver(title, testMode):
    try:
        for i in range(1, len(api_key)+1):
            script_generator_response = script_generator(title, testMode, api_key[f'account_{i}'][0])
            is_script_generated = script_generator_response[1]
            if is_script_generated:
                script = script_generator_response[0]
                return [script, i]
            else:
                print(f"account_{i} FAILED to generate the Script")
                print(script_generator_response[0])
                print(f"Trying to generate script with account_{i+1} .....")
                continue
    except Exception as e:
        print(f"Error in generating Script: {e}")

def speech_receiver(script, testMode):
    try:
        for i in range(1, len(api_key) + 1):
            speech_generated_details = text_to_speech(script, testMode, api_key[f'account_{i}'][1], api_key[f'account_{i}'][2])
            is_speech_generated = speech_generated_details[0]
            speech_path = speech_generated_details[1]
            if is_speech_generated:
                return [True, i, speech_path]
            else:
                print(f"account_{i} Failed to generate Voiceover")
                continue
        return [False, "VoiceOver NOT Generated, Error"]
    except Exception as e:
        print(f"Error in generating Voiceover: {e}")

def images_receiver(script, testMode):
    try:
        for i in range(1, len(api_key)+1):
            images_name_with_scene = main_image_function(script, testMode, api_key[f'account_{i}'][0])
            if images_name_with_scene:
                return images_name_with_scene
            else:
                print(f"Failed to get images with account_{i}")
                continue
    except Exception as e:
        print("Error in generating images: ", e)

def main(title, testMode):
    if testMode:
        print("Test Mode is ON. Only sample outputs will be provided. To disable Test Mode, set testMode = False in main.py")
    else:
        print("Test Mode is OFF. Actual APIs will be used.")
    
    # Generate script
    script_info = script_receiver(title, testMode)
    script = script_info[0]
    script_account = script_info[1]
    print(f"account_{script_account} generated Script Successfully:\n{script}")
    
    # Generate voiceover
    voiceover_info = speech_receiver(script, testMode)
    is_voiceover_generated = voiceover_info[0]
    voiceover_account = voiceover_info[1]
    audio_path = voiceover_info[2]
    if is_voiceover_generated:
        print(f"account_{voiceover_account} generated voiceover Successfully")
        print(f"Path of voiceover file: {audio_path}")
    else:
        print("Failed to generate voiceover with every account")
    
    # Generate images
    images_mapping = images_receiver(script, testMode)
    print("Images mapping is as follows:")
    print(images_mapping)
    
    # Generate Video
    generate_final_video(audio_path, images_mapping, output_filename="final_video.mp4", transition_duration=0.5)

# ---------------------------
# New: YouTube Upload Functionality
# ---------------------------
def upload_to_youtube(video_file, title, description="Don't forget to like and subscribe", tags=None, privacyStatus="public"):
    """
    Uploads the given video file to YouTube.
    Requires a client_secrets.json file in your working directory.
    """
    try:
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request

        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        credentials = None

        # Check if token.pickle exists for stored credentials.
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                credentials = pickle.load(token)
        
        # If credentials are not valid, initiate the OAuth flow.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
                credentials = flow.run_local_server(port=0)
            # Save the credentials for future use.
            with open("token.pickle", "wb") as token:
                pickle.dump(credentials, token)
        
        youtube = build("youtube", "v3", credentials=credentials)
        
        # Provide additional metadata: description, tags, and categoryId.
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": "22"  # For example, "22" is often used for People & Blogs.
            },
            "status": {
                "privacyStatus": privacyStatus
            }
        }
        
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploading... {int(status.progress() * 100)}% complete")
        
        print("Upload Complete!")
        return response
    
    except Exception as e:
        print("An error occurred during upload:", e)
        return None

# ---------------------------
# Scheduled Process Function
# ---------------------------
def process_video():
    print("Starting video generation process...")
    channel_niches = ['space facts', 'science facts', 'technology facts', 'amazing facts', 'general facts', 'knowledge facts']
    title = main_topic_generator(YOUTUBE_API_KEY, channel_niche=random.choice(channel_niches), GEMINI_API_KEY=GEMINI_API_KEY_1)
    testMode = False
    main(title, testMode)
    
    # Upload the generated video.
    print("Uploading video to YouTube...")
    response = upload_to_youtube("final_video.mp4", title)
    if response:
        print("Video uploaded successfully! Deleting local video file.")
        try:
            os.remove("final_video.mp4")
            os.rmdir("video_assets")
            print("Local video file and assets deleted.")
        except Exception as e:
            print("Failed to delete local video file:", e)
    else:
        print("Video upload failed. Local video file retained.")

# ---------------------------
# Schedule the process to run twice daily
# ---------------------------
# Schedule first upload at 2:00 PM and second at 6:00 PM
schedule.every().day.at("14:00").do(process_video)
schedule.every().day.at("18:00").do(process_video)

print("Scheduler is running. Waiting for next scheduled time...")
while True:
    schedule.run_pending()
    time.sleep(30)  # Check every 30 seconds
