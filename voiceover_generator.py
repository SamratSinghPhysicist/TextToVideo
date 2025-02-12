import requests
import os

import os
import requests

def text_to_speech(script, testMode, api_key_elevenlabs, voice_id, output_file="output_speech.mp3"):
    is_speech_generated = False
    if not testMode:
        """
        Sends text to ElevenLabs API to generate speech and saves it as an MP3 file.
        """
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Content-Type": "application/json",
            "xi-api-key": api_key_elevenlabs
        }
        data = {
            "text": script,
            "model_id": "eleven_multilingual_v2",  # Use multilingual model for Hinglish
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        print("Generating speech...")
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            # Ensure the target directory exists
            target_dir = "video_assets"
            os.makedirs(target_dir, exist_ok=True)
            # Construct the full file path within the 'video_assets' directory
            output_path = os.path.join(target_dir, output_file)
            
            with open(output_path, "wb") as f:
                f.write(response.content)
                
            print("Speech generated successfully and saved to:", output_path)
            is_speech_generated = True
            return is_speech_generated
        else:
            print("Error generating speech:")
            print(response.json())
            is_speech_generated = False
            return is_speech_generated

    else:
        print("This is Test mode. The speech for the script is generated here is only for testing. "
              "To generate the actual speech, please set testMode to False. "
              "The test speech is: /test_assets/test_voiceover.mp3")
        is_speech_generated = False
        return is_speech_generated


"""

def main(script):
    
    # Name of the output MP3 file
    output_file = "output.mp3"
    
    # Generate speech and then play it
    text_to_speech(script, output_file)

if __name__ == "__main__":
    main()

"""

