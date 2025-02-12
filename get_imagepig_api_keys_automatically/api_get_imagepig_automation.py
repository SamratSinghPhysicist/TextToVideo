import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Temp Mail API configuration
BASE_TEMPMAIL_URL = "https://mailtemp-production.up.railway.app/api"

# ImagePig Registration URL
IMAGEPIG_REGISTER_URL = "https://imagepig.com/account/registration/"

# Set up headless Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Use webdriver-manager to install and manage ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def create_temp_email():
    """Create a temporary email address using the temp mail API."""
    response = requests.post(f"{BASE_TEMPMAIL_URL}/email")
    response.raise_for_status()
    return response.json()

def get_verification_email(email_id):
    """
    Poll for a verification email from ImagePig (from oink@imagepig.com)
    and extract the verification link.
    """
    for _ in range(12):  # Poll for up to 2 minutes (12 * 10 seconds)
        response = requests.get(f"{BASE_TEMPMAIL_URL}/email/{email_id}/messages")
        response.raise_for_status()
        messages = response.json()
        
        for message in messages:
            if "oink@imagepig.com" in message.get("from", ""):
                # Ensure content is a string even if returned as a list
                content = message.get("content", "")
                if isinstance(content, list):
                    content = "".join(content)
                # Parse the email content to find the verification link
                soup = BeautifulSoup(content, "html.parser")
                for link in soup.find_all("a", href=True):
                    if link["href"].startswith("https://imagepig.com/account/verification/"):
                        return link["href"]
        time.sleep(10)
    return None

def extract_api_key():
    """
    Extract the API key from the dashboard page.
    The API key is contained inside a <mark> tag.
    """
    dashboard_html = driver.page_source
    soup = BeautifulSoup(dashboard_html, "html.parser")
    mark_tag = soup.find("mark")
    return mark_tag.text if mark_tag else None

# List to store retrieved API keys
api_keys = []

# Automate the process for 100 accounts
for i in range(5):
    print(f"[*] Creating Account {i + 1}")

    # Step 1: Create a temporary email
    temp_email_data = create_temp_email()
    temp_email = temp_email_data["address"]
    temp_email_id = temp_email_data["id"]
    print(f"[*] Temporary email created: {temp_email}")

    # Step 2: Go to the ImagePig registration page and fill the form
    driver.get(IMAGEPIG_REGISTER_URL)
    driver.find_element(By.ID, "id_email").send_keys(temp_email)
    driver.find_element(By.ID, "id_password").send_keys("Study@123")
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    print("[*] Waiting for verification email...")
    time.sleep(10)  # initial wait before polling for email

    # Step 3: Poll for the verification email and extract the verification link
    verification_link = get_verification_email(temp_email_id)
    if not verification_link:
        print("[!] Verification email not received. Skipping this account.")
        continue

    print(f"[*] Verification link received: {verification_link}")
    
    # Step 4: Verify the account by visiting the verification link
    driver.get(verification_link)
    
    # Wait for the page to load and click on "Continue to the dashboard"
    try:
        driver.find_element(By.LINK_TEXT, "Continue to the dashboard").click()
    except Exception as e:
        print("[!] Could not find the dashboard link:", e)
        continue

    time.sleep(5)  # wait for the dashboard to load

    # Step 5: Extract the API key from the dashboard
    api_key = extract_api_key()
    if api_key:
        api_keys.append(api_key)
        print(f"[+] API Key {i + 1}: {api_key}")
    else:
        print("[!] API Key not found on the dashboard.")

    # Step 6: Log out to finish this account session
    try:
        driver.find_element(By.ID, "logout").click()
    except Exception as e:
        print("[!] Could not log out:", e)
    
    time.sleep(5)  # wait before starting next account

# Save API keys to a file
with open("imagepig_api_keys.txt", "w") as f:
    for key in api_keys:
        f.write(key + "\n")

print("[*] Process completed. API keys saved to imagepig_api_keys.txt")
driver.quit()
