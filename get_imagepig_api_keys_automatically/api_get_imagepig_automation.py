import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- TempMail Class (Using Mail.tm API) ---
class TempMail:
    def __init__(self):
        self.base_url = "https://api.mail.tm"
        
    def create_account(self):
        domains_resp = requests.get(f"{self.base_url}/domains")
        domains_resp.raise_for_status()
        domains = domains_resp.json()['hydra:member']
        if not domains:
            print("No domains available")
            return None
        domain = domains[0]['domain']
        email = f"temp{int(time.time())}@{domain}"
        password = "password123"
        
        data = {"address": email, "password": password}
        response = requests.post(f"{self.base_url}/accounts", json=data)
        
        if response.status_code == 201:
            print(f"Temporary Email Created: {email}")
            token = self.login(email, password)
            if token:
                return {"email": email, "password": password, "token": token}
            else:
                return None
        else:
            print("Error creating email account.")
            return None
    
    def login(self, email, password):
        response = requests.post(f"{self.base_url}/token", json={"address": email, "password": password})
        if response.status_code == 200:
            return response.json()["token"]
        else:
            print("Error logging in.")
            return None
    
    def get_messages(self, account):
        headers = {"Authorization": f"Bearer {account['token']}"}
        response = requests.get(f"{self.base_url}/messages", headers=headers)
        
        if response.status_code == 200:
            messages = response.json()["hydra:member"]
            return messages
        else:
            print("Error fetching messages.")
            return []
    
    def get_message_details(self, account, message_id):
        headers = {"Authorization": f"Bearer {account['token']}"}
        response = requests.get(f"{self.base_url}/messages/{message_id}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print("Error fetching message details.")
            return None
# --- End TempMail Class ---

# ImagePig Registration URL
IMAGEPIG_REGISTER_URL = "https://imagepig.com/account/registration/"

# Set up headless Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Use webdriver-manager to automatically manage ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def extract_verification_link(email_content):
    # If email_content is a list, join it into a single string
    if isinstance(email_content, list):
        email_content = ''.join(email_content)
    soup = BeautifulSoup(email_content, "html.parser")
    for link in soup.find_all("a", href=True):
        if link["href"].startswith("https://imagepig.com/account/verification/"):
            return link["href"]
    return None


def extract_api_key():
    """
    Extract the API key from the dashboard page.
    The API key is inside a <mark> tag.
    """
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, "html.parser")
    mark_tag = soup.find("mark")
    if mark_tag:
        return mark_tag.text.strip()
    return None

# List to store the API keys
api_keys = []
temp_mail_service = TempMail()

# Automate the process for 1 accounts
for i in range(1):
    print(f"[*] Creating Account {i + 1}")
    account = temp_mail_service.create_account()
    if not account:
        print("[!] Failed to create temp mail account, skipping this account.")
        continue
    
    # Step 1: Register on ImagePig using the temporary email
    driver.get(IMAGEPIG_REGISTER_URL)
    driver.find_element(By.ID, "id_email").send_keys(account['email'])
    driver.find_element(By.ID, "id_password").send_keys("Study@123")
    driver.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    
    print("[*] Waiting for verification email...")
    verification_link = None
    start_time = time.time()
    
    # Poll for up to 3 minutes for the verification email
    while time.time() - start_time < 180:
        messages = temp_mail_service.get_messages(account)
        for msg in messages:
            sender = msg.get("from", {}).get("address", "")
            if "oink@imagepig.com" in sender:
                details = temp_mail_service.get_message_details(account, msg["id"])
                # Try to use HTML content; fallback to plain text if needed
                email_content = details.get("html") if details.get("html") else details.get("text", "")
                verification_link = extract_verification_link(email_content)
                if verification_link:
                    break
        if verification_link:
            break
        time.sleep(10)
    
    if not verification_link:
        print("[!] Verification email not received in time. Skipping this account.")
        continue
    
    print(f"[*] Verification link received: {verification_link}")
    
    # Step 2: Visit the verification link
    driver.get(verification_link)
    
    # Click "Continue to the dashboard" to reach the dashboard
    try:
        driver.find_element(By.LINK_TEXT, "Continue to the dashboard").click()
    except Exception as e:
        print("[!] Could not find the dashboard link:", e)
        continue

    time.sleep(5)  # Wait for the dashboard page to load
    
    # Step 3: Extract the API key from the dashboard
    api_key = extract_api_key()
    if api_key:
        api_keys.append(api_key)
        print(f"[+] API Key {i + 1}: {api_key}")
    else:
        print("[!] API Key not found on dashboard.")
    
    # Step 4: Log out from the account
    try:
        driver.find_element(By.ID, "logout").click()
    except Exception as e:
        print("[!] Could not log out:", e)
    
    time.sleep(5)

# Save all API keys to a file
with open("get_imagepig_api_keys_automatically/imagepig_api_keys.txt", "w") as f:
    for key in api_keys:
        f.write(key + "\n")

print("[*] Process completed. API keys saved to imagepig_api_keys.txt")
driver.quit()
