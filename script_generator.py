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
            prompt = "Create a script for a YouTube Shorts video that is between 30 seconds and 1 minute long. The script should be in hinglish (hindi + english both mixed).  I will be using this script in a text-to-video app, so the output should be *only* the text to be spoken.  Do not include any scene descriptions, camera directions, emotional cues, or suggestions of any kind.  Use line breaks (paragraph breaks) to indicate where I should make a visual change in my video.  The script should be concise and engaging for a short-form video format.  I want the script to be ready to be directly inputted into a text-to-video application, So don't say anything like 'Okay, here's your script, ready for text-to-video:' . The video will be about " + title + "."
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