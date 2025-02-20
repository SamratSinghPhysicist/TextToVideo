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
            prompt = f"""
            Create a script for a YouTube Shorts video that lasts between 30 seconds and 1 minute. The script should be written in Hinglish (a mix of Hindi and English) and must consist only of the dialogue to be spoken in the video. It should be concise, engaging, and ready for direct use in a text-to-video application. Also, each scene should not be more than 5 seconds long. And, each scene should be separated by a new line (\n\n) 

            Do not include any scene markers, scene descriptions, or camera directions. The script should only have the text that is spoken. Please follow the example below:

            Correct format (desired output) - Example of correct output:
            "Kya aapko pata h?

            Iceberg se collision toh hua, woh toh sabko pata h

            But real reason is steel"

            Incorrect format (what to avoid) - Example of Incorrect output:
            "Scene 1:
            Kya aapko pata h?

            Scene 2: 
            Iceberg se collision toh hua, woh toh sabko pata h

            Scene 3: 
            But real reason is steel"

            The video will be about {title}.
            """
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


# print(script_generator("2 Space facts I bet you didn't know!", False, "AIzaSyA0RYI9KRrNLi6KaX4g49UJD4G5YBEb6II"))