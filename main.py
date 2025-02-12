#Final Video Generator

from moviepy import *

from script_generator import script_generator
from voiceover_generator import text_to_speech
from image_generator import main_image_function


import os
from dotenv import load_dotenv

#Loading API keys from .env file
load_dotenv()
#API keys for account_1=samratddypppis@gmail.com
GEMINI_API_KEY_1 = os.getenv("GEMINI_API_KEY_1")

ELEVENLABS_API_KEY_1 = os.getenv("ELEVENLABS_API_KEY_1")
VOICE_ID_1 = os.getenv("VOICE_ID_1")

CSE_API_KEY_1 = os.getenv("CSE_API_KEY_1")
CSE_ID_1 = os.getenv("CSE_ID_1")

#API keys for account_2=samrat1212study2@gmail.com
GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")

ELEVENLABS_API_KEY_2 = os.getenv("ELEVENLABS_API_KEY_2")
VOICE_ID_2 = os.getenv("VOICE_ID_2")

CSE_API_KEY_2 = os.getenv("CSE_API_KEY_2")
CSE_ID_2 = os.getenv("CSE_ID_2")

#API keys for account_3=sam1212factz@gmail.com
GEMINI_API_KEY_3 = os.getenv("GEMINI_API_KEY_3")

ELEVENLABS_API_KEY_3 = os.getenv("ELEVENLABS_API_KEY_3")
VOICE_ID_3 = os.getenv("VOICE_ID_3")

CSE_API_KEY_3 = os.getenv("CSE_API_KEY_3")
CSE_ID_3 = os.getenv("CSE_ID_3")

#API Keys for different accounts
api_key = {
    'account_1': [GEMINI_API_KEY_1, ELEVENLABS_API_KEY_1, VOICE_ID_1, CSE_API_KEY_1, CSE_ID_1],
    'account_2': [GEMINI_API_KEY_2, ELEVENLABS_API_KEY_2, VOICE_ID_2, CSE_API_KEY_2, CSE_ID_2],
    'account_3': [GEMINI_API_KEY_3, ELEVENLABS_API_KEY_3, VOICE_ID_3, CSE_API_KEY_3, CSE_ID_3],
}


# testMode = True


def script_receiver(title, testMode):
    try:
        for i in range(1, len(api_key)+1):
            script_generator_response = script_generator(title, testMode, api_key[f'account_{i}'][0])
            is_script_generated = script_generator_response[1]
            if is_script_generated == True:
                script = script_generator_response[0]
                return [script, i]
            else:
                script = script_generator_response[0]
                print(f"account_{i} FAILED to generate the Script")
                print (script)
                print(f"Trying to generate script with account_{i+1} .....")
                continue
    except Exception as e:
        print(f"Error in generating Script: {e}")

def speech_receiver(script, testMode):
    try:
        for i in range(1, len(api_key) + 1):
            is_speech_generated = text_to_speech(script, testMode, api_key[f'account_{i}'][1], api_key[f'account_{i}'][2])

            if is_speech_generated == True:
                return [True, i]
            else:
                print(f"account_{i} Failed to generate Voiceove")
        return [False, "VoiceOver NOT Generated, Error"]
    except Exception as e:
        print(f"Error in generating Voiceover: {e}")

def images_receiver(script, testMode):
    try:
        for i in range (1, len(api_key)+1):
            images_name_with_scene = main_image_function(script, testMode, api_key[f'account_{i}'][0], api_key[f'account_{i}'][3], api_key[f'account_{i}'][4])

            if images_name_with_scene:
                return [images_name_with_scene, i]
            else:
                print(f"Failed to get images with account_{i}")
                continue
    except Exception as e:
        print("Error in generating images: ", e)


def main(title, testMode):
    if testMode == False:
        print("Test Mode is Off. APIs will be USED")
    else:
        print("Test Mode is ON. Only Sample outputs would be provided. No APIs will be used.\n To turn off Test Mode set testMode = False, in main.py")
    # Generate script
    script_info = script_receiver(title, testMode)
    script = script_info[0]
    script_account = script_info[1]
    print(f"account_{script_account} generated Script Successfully: \n {script}")
    
    #Generate voiceover
    voiceover_info = speech_receiver(script, testMode)
    is_voiceover_generated = voiceover_info[0]
    voiceover_account = voiceover_info[1]
    if is_voiceover_generated == True:
        print(f"account_{voiceover_account} generated voiceover Successfully")
    else:
        print("Failed to generate voiceover with every account")

    # Generate Images
    images_info = images_receiver(script, testMode)
    images_name_with_scene = images_info[0]
    image_account = images_info[1]

    print(f"Images generated with account_{image_account}.\n Here are the images name for each scene:\n {images_name_with_scene}")



if __name__ == '__main__':
    title = "3 Facts about unicorn"
    testMode = False
    main(title, testMode)
