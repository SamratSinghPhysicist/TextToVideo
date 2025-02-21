import requests
import re
from base64 import b64decode
from pathlib import Path
import random

from script_generator import generate_gemini


def split_script_into_scenes(script):
    """
    Splits a script into scenes.
    Assumes that each scene is separated by one or more blank lines.
    """
    # The regex pattern '\n\s*\n' matches a newline, any whitespace (if any), and another newline.
    scenes_list = re.split(r'\n\s*\n', script.strip())
    print(scenes_list)
    return scenes_list

def image_generate_prompt_pollinations(scene, api_key_gemini):
    prompt = f"""I have a scene description. Please convert this into a detailed and vivid image-generation prompt suitable for an AI art generator. Make sure to include key visual elements such as the setting, mood, characters, lighting, and any distinctive features that capture the essence of the scene. The prompt should be concise yet descriptive enough to generate a faithful illustration. Also, just give the prompt and don't say anything else as I would directly use this in text to image converter, So, just give the prompt and say nothing else. Also, the prompt should not be too long. Keep it consise. The scene is below: {scene}"""
    
    image_generate_prompt = generate_gemini(prompt, api_key_gemini)

    image_generate_prompt = image_generate_prompt.replace('\\', ' ')
    image_generate_prompt = image_generate_prompt.replace('\n', ' ')

    return image_generate_prompt

def generate_image_pollinations_ai(prompt, testMode, width=1080, height=1920, seed=random.randint(1,100000), model='flux'):
    if testMode == False:
        # Define the subfolder and filename
        subfolder = Path("video_assets")
        # Create the subfolder if it doesn't exist
        subfolder.mkdir(parents=True, exist_ok=True)

        # Clean up prompt to be used as a file name
        for char in [' ', ',', '/', '\\', '!', '\n', '.', ';', '?', ':', '\'', '"', '`', '~', '@', '#', '$', '%', '^', '&', '*', '=', '>', '<']:
            prompt = prompt.replace(char, '_')
        
        # Define the full file path where the image will be saved
        filepath = f"video_assets/{prompt}.jpg"
        # Make sure the filename is not overly long
        safe_filepath = f"{filepath[:25]}.jpg"
        image_path = safe_filepath

        def download_image(image_url, image_path):
            try:
                response = requests.get(image_url)
            except Exception as e:
                print("Error during requests.get:", e)
                print("Using test_assests/placeholder.jpg")
                return "test_assets/placeholder.jpg"

            # Check if the request was successful
            if response.status_code == 200 and response.content:
                with open(image_path, 'wb') as file:
                    file.write(response.content)
                
                # Verify the file size is reasonable (i.e., not an empty or near-empty file)
                file_size = Path(image_path).stat().st_size
                if file_size < 500:  # adjust this threshold if needed
                    print("Downloaded image is too small (likely invalid). Using placeholder image.")
                    return "test_assets/placeholder.jpg"
                else:
                    print("Download Completed")
                    return image_path
            else:
                print("Failed to download image for this scene. Using test_assests/placeholder.jpg")
                return "test_assets/placeholder.jpg"

        image_url = f"https://pollinations.ai/p/{prompt}?width={width}&height={height}&seed={seed}&model={model}"
        path_of_downloaded_image = download_image(image_url, image_path)
        return path_of_downloaded_image

    else:
        print("Test Mode is ON. Placeholder images will be used.")
        print("Path of placeholder.jpg: /test_assets/placeholder.jpg")
        return "test_assets/placeholder.jpg"

def main_image_function(script, testMode, api_key_gemini):
    # Split the script into a list of scenes
    scenes_list = split_script_into_scenes(script)
    image_name_with_scene = {}

    if testMode == False:
        try:
            for i in range(0, len(scenes_list)):
                prompt_text = image_generate_prompt_pollinations(scenes_list[i], api_key_gemini)
                image_path = generate_image_pollinations_ai(prompt_text, testMode)
                image_name_with_scene.update({f"scene{i+1}": image_path})

            return image_name_with_scene
        except Exception as e:
            print("Error in generating Image:", e)
    else:
        print("Test Mode is ON")
        print("Skipping the image search and download process, and using placeholder images")
        print("To turn off the Test Mode, change the testMode variable to False in main_image_function()")
        for i in range(1, len(scenes_list) + 1):
            image_name_with_scene.update({f"scene{i}": "test_assets/placeholder.jpg"})
        return image_name_with_scene
























"""
def download_image(image_url, image_path):
    # Fetching the image from the URL
    response = requests.get(image_url)

    #Downloading and saving the image
    # with open(f'pollinations_images/{img_name}.jpg', 'wb') as file:
    with open(f'{image_path}', 'wb') as file:
        file.write(response.content)
    # Logging completion message
    print('Download Completed')

# Image details
prompt = 'A beautiful landscape'
width = 1080
height = 1920

seed = random.randint(1, 100) # Each seed generates a new image variation
model = 'flux' # Using 'flux' as default if model is not provided

image_url = f"https://pollinations.ai/p/{prompt}?width={width}&height={height}&seed={seed}&model={model}"

download_image(image_url, "TestImg")
"""