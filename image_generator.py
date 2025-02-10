
"""

IT IS NOT COMPLETE YET. I WILL UPDATE IT SOON.


IT IS NOT COMPLETE YET. I WILL UPDATE IT SOON.


IT IS NOT COMPLETE YET. I WILL UPDATE IT SOON.


IT IS NOT COMPLETE YET. I WILL UPDATE IT SOON.

"""








import requests
from googleapiclient.discovery import build


# Replace these with your own API key and CSE ID
CSE_API_KEY = 'AIzaSyAHK4qMoAWDk283bx89ho4l3Eq1v8D09m4'
CSE_ID = 'c2f46cbbd07374a55'


def google_image_search(CSE_API_KEY, cse_id, query):
    """
    Searches for images using Google's Custom Search API and returns the top result.
    """
    service = build("customsearch", "v1", developerKey=CSE_API_KEY)
    
    # Perform the search with searchType set to "image"
    res = service.cse().list(
        q=query,
        cx=cse_id,
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