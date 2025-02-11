import requests
from googleapiclient.discovery import build

from script_generator import script_generator
import re
from DuckDuckGo_API import generateDDG_ai_chat


# Replace these with your own API key and CSE ID
CSE_API_KEY = 'AIzaSyAHK4qMoAWDk283bx89ho4l3Eq1v8D09m4'
CSE_ID = 'c2f46cbbd07374a55'


def split_script_into_scenes(script):
    """
    Splits a script into scenes.
    Assumes that each scene is separated by one or more blank lines.
    """
    # The regex pattern '\n\s*\n' matches a newline, any whitespace (if any), and another newline.
    scenes_list = re.split(r'\n\s*\n', script.strip())
    return scenes_list

def image_search_query_for_only_a_single_scene(scene):
    
    promt = f"Write 2-3 relevant keywords (in a single line) for google image search to get relevant images as per this scene lines: {scene}. Note that you just have to write the keywords, nothing else. I just want the text as I will directly use it through a code to get images. Don't give any instructions, or directions, or tell what you are writing. Just give me the one line keywords."
    search_query = generateDDG_ai_chat(promt, "gpt-4o-mini")

    return search_query


def google_image_search(CSE_API_KEY, CSE_ID, query):
    """
    Searches for images using Google's Custom Search API and returns the top result.
    """
    service = build("customsearch", "v1", developerKey=CSE_API_KEY)
    
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

def download_image(image_url, filename):
    """
    Downloads an image from a URL and saves it to a file.
    """
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Raise an error on bad status
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Image successfully downloaded: {filename}")
    except Exception as e:
        print("Error downloading image:", e)


"""
def main(script):
    #Different Scenes into a list
    scenes_list = split_script_into_scenes(script)

    #Search Query, Link, and Download for each image
    for i in scenes_list:
        search_query = image_search_query_for_only_a_single_scene(i)

        result = google_image_search(CSE_API_KEY, CSE_ID, search_query)

        if result:
            #Get link of image
            image_url = result.get('link')
            print(f"Top image URL for {search_query} is: {image_url}")

            #Download the image and save it
            image_name_to_be_saved_as = search_query.replace(' ', '_')
            download_image(image_url, f"{image_name_to_be_saved_as}.jpg")
        else:
            print("No image was found")
        


if __name__ == '__main__':
    title = input("Enter the title of Video: ")
    script = script_generator(title)  #But, Don't use it here, use it directly in main video maker file, to avoid different scripts
    main(script)
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
