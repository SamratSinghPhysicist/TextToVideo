#Final Video Generator
from script_generator import script_generator
from voiceover_generator import text_to_speech
from image_generator import main_image_function
from video_generator import generate_final_video

import os
from dotenv import load_dotenv

import asyncio


#Loading API keys from .env file
load_dotenv()
#API keys for account_1=samratddypppis@gmail.com
GEMINI_API_KEY_1 = os.getenv("GEMINI_API_KEY_1")

ELEVENLABS_API_KEY_1 = os.getenv("ELEVENLABS_API_KEY_1")
VOICE_ID_1 = os.getenv("VOICE_ID_1")


#API keys for account_2=samrat1212study2@gmail.com
GEMINI_API_KEY_2 = os.getenv("GEMINI_API_KEY_2")

ELEVENLABS_API_KEY_2 = os.getenv("ELEVENLABS_API_KEY_2")
VOICE_ID_2 = os.getenv("VOICE_ID_2")


#API keys for account_3=sam1212factz@gmail.com
GEMINI_API_KEY_3 = os.getenv("GEMINI_API_KEY_3")

ELEVENLABS_API_KEY_3 = os.getenv("ELEVENLABS_API_KEY_3")
VOICE_ID_3 = os.getenv("VOICE_ID_3")


IMAGEPIG_API_KEY = os.getenv("IMAGEPIG_API_KEY")


#API keys for account_4=samrat1212study@gmail.com
GEMINI_API_KEY_4 = "NOT MADE YET"

ELEVENLABS_API_KEY_4 = os.getenv("ELEVENLABS_API_KEY_4")
VOICE_ID_4 = os.getenv("VOICE_ID_4")



#API Keys for different accounts
api_key = {
    'account_1': [GEMINI_API_KEY_1, ELEVENLABS_API_KEY_1, VOICE_ID_1, IMAGEPIG_API_KEY],
    'account_2': [GEMINI_API_KEY_2, ELEVENLABS_API_KEY_2, VOICE_ID_2, IMAGEPIG_API_KEY],
    'account_3': [GEMINI_API_KEY_3, ELEVENLABS_API_KEY_3, VOICE_ID_3, IMAGEPIG_API_KEY],
    'account_4': [GEMINI_API_KEY_4, ELEVENLABS_API_KEY_4, VOICE_ID_4, IMAGEPIG_API_KEY]
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
            speech_generated_details = text_to_speech(script, testMode, api_key[f'account_{i}'][1], api_key[f'account_{i}'][2])
            is_speech_generated = speech_generated_details[0]
            speech_path = speech_generated_details[1]

            if is_speech_generated == True:
                return [True, i, speech_path]
            else:
                print(f"account_{i} Failed to generate Voiceover")
                continue
        return [False, "VoiceOver NOT Generated, Error"]
    except Exception as e:
        print(f"Error in generating Voiceover: {e}")

def images_receiver(script, testMode):
    try:
        for i in range (1, len(api_key)+1):
            images_name_with_scene = main_image_function(script, testMode, api_key[f'account_{i}'][0])

            if images_name_with_scene:
                return images_name_with_scene
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
    audio_path = voiceover_info[2]
    if is_voiceover_generated == True:
        print(f"account_{voiceover_account} generated voiceover Successfully")
        print(f"Path of voiceover file: {audio_path}")
    else:
        print("Failed to generate voiceover with every account")

    # Generate Images
    images_mapping = images_receiver(script, testMode)
    print("Images mapping is as follows:")
    print(images_mapping)

    #Generate Video
    generate_final_video(audio_path, images_mapping, output_filename="final_video.mp4", transition_duration=0.5)



if __name__ == '__main__':
    title = "Frilled neck lizard 🦎 #trending #facts #sciencefacts #science #australia  #viral #lizard #shorts"
    testMode = False
    main(title, testMode)
