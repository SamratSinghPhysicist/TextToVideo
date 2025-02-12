import requests
import re
from base64 import b64decode
from pathlib import Path
import asyncio

from script_generator import generate_gemini



def split_script_into_scenes(script):
    """
    Splits a script into scenes.
    Assumes that each scene is separated by one or more blank lines.
    """
    # The regex pattern '\n\s*\n' matches a newline, any whitespace (if any), and another newline.
    scenes_list = re.split(r'\n\s*\n', script.strip())
    print (scenes_list)
    return scenes_list

def image_generate_prompt_imagepig(scene, api_key_gemini):
    prompt = f"""I have a scene description. Please convert this into a detailed and vivid image-generation prompt suitable for an AI art generator. Make sure to include key visual elements such as the setting, mood, characters, lighting, and any distinctive features that capture the essence of the scene. The prompt should be concise yet descriptive enough to generate a faithful illustration. Also, just give the prompt and don't say anything else as I would directly use this in text to image converter, So, just give the prompt and say nothing else. The scene is below: {scene}"""
    
    image_generate_prompt = generate_gemini(prompt, api_key_gemini)

    image_generate_prompt = image_generate_prompt.replace('\\', ' ')
    image_generate_prompt = image_generate_prompt.replace('\n', ' ')

    return image_generate_prompt

def generate_imagepig_ai(prompt, testMode, IMAGEPIG_API_KEY):

    if testMode == False:
        r = requests.post(
            "https://api.imagepig.com/flux",
            headers={"Api-Key": IMAGEPIG_API_KEY},
            json={"prompt": prompt},
        )

        if r.ok:
            # Define the subfolder and filename
            subfolder = Path("video_assets")
            # Create the subfolder if it doesn't exist
            subfolder.mkdir(parents=True, exist_ok=True)

            prompt = prompt.replace(' ', '_')
            prompt = prompt.replace(',', '_')
            prompt = prompt.replace('/', '_')
            prompt = prompt.replace('\\', '_')
            prompt = prompt.replace('!', '_')
            prompt = prompt.replace('\n', '_')
            prompt = prompt.replace('.', '_')
            prompt = prompt.replace(';', '_')
            prompt = prompt.replace('?', '_')
            prompt = prompt.replace(':', '_')
            prompt = prompt.replace('\'', '_')
            prompt = prompt.replace('"', '_')
            prompt = prompt.replace('`', '_')
            prompt = prompt.replace('~', '_')
            prompt = prompt.replace('@', '_')
            prompt = prompt.replace('#', '_')
            prompt = prompt.replace('$', '_')
            prompt = prompt.replace('%', '_')
            prompt = prompt.replace('^', '_')
            prompt = prompt.replace('&', '_')
            prompt = prompt.replace('*', '_')
            prompt = prompt.replace('=', '_')
            prompt = prompt.replace('>', '_')
            prompt = prompt.replace('<', '_')
            # Define the full file path where the image will be saved
            filepath = f"video_assets/{prompt}.jpg"
            safe_filepath = f"{filepath[:20]}.jpg"

            # Save the image to the specified path
            with open(safe_filepath, "wb") as f:
                f.write(b64decode(r.json()["image_data"]))
    
            print("Image download successful")
            image_path = safe_filepath
            return image_path
        else:
            r.raise_for_status()
            return "Failed to download the image"

    else:
        print("Test Mode is ON. placeholder images will be used")
        print("Path of placeholder.jpg: /video_assets/placeholder.jpg")
        image_path = "test_assets/placeholder.jpg"
        return image_path



async def main_image_function(script, testMode, api_key_gemini, IMAGEPIG_API_KEY):
    #Different Scenes into a list
    scenes_list = split_script_into_scenes(script)

    image_name_with_scene = {}

    if testMode == False:
        try:
            for i in range(0, len(scenes_list)):
                image_generate_prompt_imagepig_ai = image_generate_prompt_imagepig(scenes_list[i], api_key_gemini)
                imagepig_image_path = generate_imagepig_ai(image_generate_prompt_imagepig_ai, testMode, IMAGEPIG_API_KEY)
                image_name_with_scene.update({f"scene{i+1}": f"{imagepig_image_path}"})

                print("Waiting for next 121 seconds due to API limits of ImagePig")
                await asyncio.sleep(121)  # Wait 121 seconds before generating other image (as were using Flux ImagePig Generator free tier)
                print("Wait over for image pig, continuing ....")

            return image_name_with_scene
        except Exception as e:
            print("Error in generating Image: ", e)

    else:
        print("Test Mode is ON")
        print("Skipping the image search and download process, and using placeholder images")
        print("To Turn off the Test Mode, change the testMode variable to False in main_image_function() function")

        for i in range (1, len(scenes_list)+1):
            image_name_with_scene.update({f"scene{i}": "test_assets/placeholder.jpg"})

        return image_name_with_scene


        














"""

if __name__ == '__main__':
    
    # Define your search query
    query = "sunset over mountains"
    
    # Search for the image
    result = google_image_search(CSE_API_KEY, CSE_ID, query)
    
    if result:
        image_url = result.get('link')
        print("Top Image URL:", image_url)
        
        # Download the image and save it as "downloaded_image.jpg"
        download_image(image_url, "downloaded_image.jpg")
    else:
        print("No image was found for the query.")

"""
