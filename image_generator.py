import requests
from googleapiclient.discovery import build
import os
import re

# from DuckDuckGo_API import generateDDG_ai_chat
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

def image_search_query_for_only_a_single_scene(scene, api_key_gemini):
    
    prompt = f"Write 2-3 relevant keywords (in a single line) for google image search to get relevant images as per this scene lines: {scene}. Note that you just have to write the keywords, nothing else. I just want the text as I will directly use it through a code to get images. Don't give any instructions, or directions, or tell what you are writing. Just give me the one line keywords."
    # search_query = generateDDG_ai_chat(promt, "gpt-4o-mini")

    search_query = generate_gemini(prompt, api_key_gemini)

    return search_query


def google_image_search(CSE_API_KEY, CSE_ID, query):
    """
    Searches for images using Google's Custom Search API and returns the top result.
    """
    service = build("customsearch", "v1", developerKey=CSE_API_KEY)
    
    try: 

    # Perform the search with searchType set to "image"
        res = service.cse().list(
            q=query,
            cx=CSE_ID,
            searchType="image",
            num=1  # Only need the top image result
        ).execute()

        # Check if any items were returned
        if 'items' in res:
            # Return the first result
            return res['items'][0]
        else:
            print("No image results found for query:", query)
            return None
    except Exception as e:
        print(f"Error in search images: {e}")

def download_image(image_url, filename):
    """
    Downloads an image from a URL and saves it to a file in the 'video_assets' subfolder.
    """
    # Define the target directory
    target_dir = 'video_assets'
    
    # Create the directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Build the full file path
    filepath = os.path.join(target_dir, filename)
    
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Raise an error on bad status
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
                
        print(f"Image successfully downloaded: {filepath}")
        return True
    except Exception as e:
        print("Error downloading image:", e)
        return False



def main_image_function(script, testMode, api_key_gemini, CSE_API_KEY, CSE_ID):
    #Different Scenes into a list
    scenes_list = split_script_into_scenes(script)

    image_name_with_scene = {}

    if testMode == False:
        #Search Query, Link, and Download for each image

        for i in range(0, len(scenes_list)):
            search_query = image_search_query_for_only_a_single_scene(scenes_list[i], api_key_gemini)

            result = google_image_search(CSE_API_KEY, CSE_ID, search_query)

            if result:
                #Get link of image
                image_url = result.get('link')
                print(f"Top image URL for {search_query} is: {image_url}")

                #Download the image and save it
                image_name_to_be_saved_as = search_query.replace(' ', '_')
                image_name_to_be_saved_as = image_name_to_be_saved_as.replace('\n', '')
                image_name_to_be_saved_as = image_name_to_be_saved_as.replace(',', '_')
                is_image_donwloaded = download_image(image_url, f"{image_name_to_be_saved_as}.jpg")
                if is_image_donwloaded == True:
                    image_name_with_scene.update({f"scene{i+1}": f"/video_assets/{image_name_to_be_saved_as}.jpg"})
                else:
                    print(f"Failed to download image for scene {i+1}")
                    print(f"Using placeholder.jpg for scene{i+1}")
                    image_name_with_scene.update({f"scene{i+1}": "/video_assets/placeholder.jpg"})

                    print (image_name_with_scene)
                    return image_name_with_scene    
            else:
                print(f"No image was found for scene{i+1}, or there was an error")
                print(f"Using placeholder.jpg for scene{i+1}")
                image_name_with_scene.update({f"scene{i+1}": "/video_assets/placeholder.jpg"})
        
    else:
        print("Test Mode is ON")
        print("Skipping the image search and download process, and using placeholder images")
        print("To Turn off the Test Mode, change the testMode variable to False in main_image_function() function")

        for i in range (1, len(scenes_list)+1):
            image_name_with_scene.update({f"scene{i+1}": "/test_assets/placeholder.jpg"})

        return image_name_with_scene
        
# main_image_function(generate_gemini("2 Facts about unicorn", 'AIzaSyBT9nNewIYud_hrVlBI_9lqqqa58REqw2Y'), False, 'AIzaSyBT9nNewIYud_hrVlBI_9lqqqa58REqw2Y', 'AIzaSyAHK4qMoAWDk283bx89ho4l3Eq1v8D09m4','c2f46cbbd07374a55')


"""
if __name__ == '__main__':
    title = input("Enter the title of Video: ")
    script = script_generator(title)  #But, Don't use it here, use it directly in main video maker file, to avoid different scripts
    main_image_function(script)
"""














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
