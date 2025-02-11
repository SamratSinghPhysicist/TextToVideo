#Final Video Generator

from moviepy import *

from script_generator import script_generator
from voiceover_generator import text_to_speech
from image_generator import main_image_function


import os
from dotenv import load_dotenv

#Loading API keys from .env file
load_dotenv()
#API keys for samratddypppis@gmail.com
GEMINI_API_KEY_1 = os.getenv("GEMINI_API_KEY")

ELEVENLABS_API_KEY_1 = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID_1 = os.getenv("VOICE_ID")

CSE_API_KEY_1 = os.getenv("CSE_API_KEY")
CSE_ID_1 = os.getenv("CSE_ID")


testMode = True


def main(title, testMode):
    # Generate script
    script = script_generator(title, testMode)

    # Generate voiceover
    text_to_speech(script, testMode)

    # Generate images
    main_image_function(script, testMode)

    # Generate video
    # video_generator(script)