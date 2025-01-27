import time
from playwright.sync_api import sync_playwright

def run_idealista_scraper():
    with sync_playwright() as p:
        # Launch Firefox browser
        browser = p.firefox.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            viewport={"width": 1366, "height": 768},
            locale="it-IT",
            geolocation={"latitude": 41.9028, "longitude": 12.4964},  # Rome, Italy
            permissions=["geolocation", "notifications"],  # Valid permissions
            timezone_id="Europe/Rome",
        )

        # Remove automation-related properties
        context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """
        )

        page = context.new_page()

        try:
            # Navigate to idealista.it
            page.goto("https://www.idealista.it")
            time.sleep(2)  # Wait for 2 seconds

            # Click the "Accetta e chiudi" button
            page.click("#didomi-notice-agree-button")
            time.sleep(60)  # Wait for 5 seconds

        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run_idealista_scraper()
