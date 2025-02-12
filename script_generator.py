#Generate Script for the given input title

from google import genai

def generate_gemini(prompt, api_key_gemini):
    client = genai.Client(api_key=api_key_gemini)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents= prompt,
    )
    # title = response.text
    print(response.text)
    return response.text

def script_generator(title, testMode, api_key_gemini):
    is_script_generated = False
    try:

        if testMode == False:
            prompt = f"Create a script for a YouTube Shorts video that lasts between 30 seconds and 1 minute. The script should be written in Hinglish (a mix of Hindi and English) and must be divided into multiple scenes. Use a blank line (i.e. two newline characters) to separate each scene. Only include the text that will be spoken in the video—do not include any camera directions, scene descriptions, or emotional cues. Don't say anything like Here is your generated script, or don't give any scene descriptions like this is Scene 1, that is scene 2, etc. The script should be concise, engaging, and ready to be directly used in a text-to-video application. The video will be about {title}."
            script = generate_gemini(prompt, api_key_gemini)
            is_script_generated = True
        else:
            script = "This is Test mode script.\n\n. The script for the video about " + title + " is generated here is only for testing.\n\n To generate the actual script, please set testMode to False."
            is_script_generated = True
        return [script, is_script_generated]
    except Exception as e:
        # print("Error in generating script: ", e)
        is_script_generated = False
        return [f"Failed to generate script. Error \n: {e}", is_script_generated]