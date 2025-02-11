import requests
from pydub import AudioSegment
from pydub.playback import play

#Importing a fucntion from the file ./script_generator.py
from script_generator import script_generator

# Replace with your actual ElevenLabs API key
ELEVENLABS_API_KEY = "sk_6718bab9e714d9eee4cbd6bce21f3d5140ed2faed553a96d"

# Select a realistic male voice; change the voice ID if needed
VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Example voice ID

def text_to_speech(script, testMode, output_file="output_speech.mp3"):
    if testMode == False:
        """
        Sends text to ElevenLabs API to generate speech and saves it as an MP3 file.
        """
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        headers = {
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
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
            with open(output_file, "wb") as f:
                f.write(response.content)
            print("Speech generated successfully and saved to:", output_file)
        else:
            print("Error generating speech:")
            print(response.json())
        
    else:
        print("This is Test mode. The speech for the script is generated here is only for testing. To generate the actual speech, please set testMode to False. The test speech is: test_voiceover.mp3")



"""

def main(script):
    
    # Name of the output MP3 file
    output_file = "output.mp3"
    
    # Generate speech and then play it
    text_to_speech(script, output_file)

if __name__ == "__main__":
    main()

"""

