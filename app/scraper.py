from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import pymongo
import os
from dotenv import load_dotenv
import requests


# Load environment variables
load_dotenv()

# Twitter/X Credentials from .env
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
MONGO_DB_URI = os.getenv("MONGO_DB_URI")

client = pymongo.MongoClient(MONGO_DB_URI)
db = client["stir"]
collection = db["trending_topics"]

# ProxyScrape - Get a free proxy
def get_proxyscrape_proxy():
    url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=1000&country=all"
    response = requests.get(url)
    proxies = response.text.strip().split('\n')

    for proxy in proxies:
        try:
            res = requests.get("https://x.com", proxies={"http": f"http://{proxy}"}, timeout=5)
            if res.status_code == 200:
                print(f"Working Proxy: {proxy}")
                return proxy.strip()
        except Exception as e:
            print(f"Proxy failed: {proxy} - {e}")
            continue
    return None

# Fetch Public IP to verify proxy
def get_public_ip():
    try:
        return requests.get("http://ipinfo.io/ip").text.strip()
    except:
        return "Unknown"

# Scraper Function
def fetch_trending_topics(proxy_failed=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    # Use proxy only if proxy_failed is False
    if not proxy_failed:
        PROXY = get_proxyscrape_proxy()
        if PROXY:
            options.add_argument(f'--proxy-server={PROXY}')
            print(f"Using Proxy: {PROXY}")
        else:
            print("No working proxy found. Using direct connection...")
    
    # Start Selenium WebDriver
    driver = webdriver.Chrome(options=options)

    try:
        # 1. Navigate to X/Twitter login page
        driver.get("https://x.com/login")
        time.sleep(3)

        # 2. Enter email/username
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username"]'))
        )
        email_field.send_keys(TWITTER_EMAIL)
        email_field.send_keys(Keys.RETURN)
        time.sleep(2)

        # 3. Enter username if prompted
        try:
            username_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//input[@name="text"]'))
            )
            username_field.send_keys(TWITTER_USERNAME)
            username_field.send_keys(Keys.RETURN)
            print("Entered Username")
        except:
            print("Username prompt not required")

        # 4. Enter password
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="password"]'))
        )
        password_field.send_keys(TWITTER_PASSWORD)
        password_field.send_keys(Keys.RETURN)
        time.sleep(5)

        # 5. Go to home timeline
        driver.get("https://x.com/home")
        time.sleep(5)

        # 6. Find the trending section
        try:
            trending_section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@aria-label, "Timeline: Trending now")]'))
            )
            print("Trending section found.")

            # Click "Show more" if available
            show_more_button = trending_section.find_element(By.XPATH, './/span[text()="Show more"]')
            show_more_button.click()
            print("Clicked 'Show more' button.")
        except Exception as e:
            print(f"'Show more' button not found. Error: {e}")

        # 7. Click on "Trending" tab
        try:
            trending_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Trending"]'))
            )
            trending_tab.click()
            print("Clicked on 'Trending' tab.")
        except:
            print("'Trending' tab not found or already active.")

        # 8. Fetch trending topics
        time.sleep(5)
        try:
            trending_topics = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//div[contains(@aria-label, "Timeline: Explore")]//span[contains(text(), "#")]')
                )
            )
            # Extract top 5 unique trends
            trends = list(dict.fromkeys([span.text for span in trending_topics]))[:5]
        except:
            print("Could not fetch trending topics.")
            trends = []

        # 9. Get public IP for verification
        public_ip = get_public_ip()

        # 10. Save to MongoDB
        if trends:
            document = {
                "timestamp": datetime.now(),
                "topics": trends,
                "ip_address": public_ip
            }
            collection.insert_one(document)
            print(f"Trending topics saved to MongoDB: {trends} from IP: {public_ip}")
            return trends
        else:
            print("No trends found to save.")
            return []

    except Exception as e:
        print("Error during scraping:", e)
        # If proxy fails, retry without proxy
        if "ERR_TUNNEL_CONNECTION_FAILED" in str(e) and not proxy_failed:
            print("Retrying without proxy...")
            return fetch_trending_topics(proxy_failed=True)
        return []

    finally:
        driver.quit()


if __name__ == "__main__":
    fetch_trending_topics()
