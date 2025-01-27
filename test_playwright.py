import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

with sync_playwright() as p:
    # Launch the browser with DevTools open
    browser = p.chromium.launch(headless=False, devtools=True)
    context = browser.new_context()
    page = context.new_page()

    # Apply stealth mode
    stealth_sync(page)

    # Navigate to google.com
    page.goto("https://www.google.com")
    time.sleep(2)  # Wait for 2 seconds

    # Navigate to idealista.com
    page.goto("https://www.idealista.com")
    time.sleep(2)  # Wait for 2 seconds

    # Navigate to idealista.it
    page.goto("https://www.idealista.it")
    time.sleep(15)  # Wait for 15 seconds for manual HAR download

    # Close the browser
    browser.close()




