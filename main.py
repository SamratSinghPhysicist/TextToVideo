import os
import pickle
import random
import shutil
from script_generator import script_generator
from voiceover_generator import text_to_speech
from image_generator import main_image_function
from video_generator import generate_final_video
from topic_fetcher import main_topic_generator



# API keys for account_1=samratddypppis@gmail.com

GEMINI_API_KEY_1 = "AIzaSyBT9nNewIYud_hrVlBI_9lqqqa58REqw2Y"

ELEVENLABS_API_KEY_1 = "sk_6718bab9e714d9eee4cbd6bce21f3d5140ed2faed553a96d"
VOICE_ID = "pNInz6obpgDQGcFmaJgB"

# API keys for account_2=samrat1212study2@gmail.com
GEMINI_API_KEY_2 = "AIzaSyA0RYI9KRrNLi6KaX4g49UJD4G5YBEb6II"

ELEVENLABS_API_KEY_2 = "sk_4f4adae16d2763397bd06db5b3441789a3c41556e4ec7ee7"



# API keys for account_3=sam1212factz@gmail.com

GEMINI_API_KEY_3 = "AIzaSyDp2PpmrRg821UXq-5NznKDCfqrFFuqa9A"

ELEVENLABS_API_KEY_3 = "sk_dd2557c5cd543fe0c60256807a3d7cddbb1991e10e433467"

YOUTUBE_API_KEY = "AIzaSyAgLCRVl5QHj51uNaSN-0ruU1UQVgHZpbc"

# API keys for account_4=samrat1212study@gmail.com
GEMINI_API_KEY_4 = "NOT MADE YET"

ELEVENLABS_API_KEY_4 = "sk_89bd9f9a40e0803b424ecbf736ae7c07f870b0231f8ff63a"


#API keys for account_5=z8q7uo@edny.net
GEMINI_API_KEY_5= "NOT MADE YET"
ELEVENLABS_API_KEY_5 = "sk_012c730771d0a09bbcf52a7fde6b4c86166af98eb1100797"



#API keys for account_6=g3tljg@edny.net
GEMINI_API_KEY_6= "NOT MADE YET"

ELEVENLABS_API_KEY_6 = "sk_001031063608d5efd044e051a0707757fe9f3b75c383ad23"

#API keys for account_7=6c6t76@edny.net
GEMINI_API_KEY_7= "NOT MADE YET"

ELEVENLABS_API_KEY_7 = "sk_6267995b417e44203acba1ab092bc54b4474d52b78301237"



# API Keys for different accounts
api_key = {
    'account_1': [GEMINI_API_KEY_1, ELEVENLABS_API_KEY_1, VOICE_ID, ],
    'account_2': [GEMINI_API_KEY_2, ELEVENLABS_API_KEY_2, VOICE_ID, ],
    'account_3': [GEMINI_API_KEY_3, ELEVENLABS_API_KEY_3, VOICE_ID, ],
    'account_4': [GEMINI_API_KEY_4, ELEVENLABS_API_KEY_4, VOICE_ID, ],
    'account_5': [GEMINI_API_KEY_5, ELEVENLABS_API_KEY_5, VOICE_ID, ],
    'account_6': [GEMINI_API_KEY_6, ELEVENLABS_API_KEY_6, VOICE_ID, ],
    'account_7': [GEMINI_API_KEY_7, ELEVENLABS_API_KEY_7, VOICE_ID, ],
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

        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                credentials = pickle.load(token)
            print("Token loaded. Valid:", credentials.valid, "Expired:", credentials.expired)

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
                "categoryId": "28"  # For example, "28" is often used for Science & Technology.
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
    title = main_topic_generator(GEMINI_API_KEY=GEMINI_API_KEY_1)
    print(f"Generated Title: {title}")

    testMode = False   #Set testMode=False to actually use APIs (For production)
    main(title, testMode)

    video_file = "final_video.mp4"
    if not os.path.exists(video_file):
        print(f"Error: Video file {video_file} not found. Upload skipped.")
        return
    print("Uploading video to YouTube...")
    response = upload_to_youtube(video_file, title)
    if response:
        print("Video uploaded successfully!")
        print("Response snippet:", response.get("snippet", {}))
        print("Deleting the local video files")
        try:
            os.remove("final_video.mp4")
            shutil.rmtree("video_assets")
            print("Local video file and assets deleted.")
        except Exception as e:
            print("Failed to delete local video file:", e)
    else:
        print("Video upload failed. Local video file retained.")

if __name__ == "__main__":
    process_video()
