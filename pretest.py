import time
import random
import os
import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from import_sqlite import import_json_to_sqlite
from scraping import  extract_house_details

def fetch_html_from_pagination(data_list, download_html='download_html'):
    """
    Fetches paginated HTML content from Idealista and returns an open browser session.
    
    Returns:
        browser (Playwright browser instance)
        context (Playwright browser context)
        page (Playwright page instance)
    """
    if not os.path.exists(download_html):
        os.makedirs(download_html)

    p = sync_playwright().start()
    
    # Step 1: Launch headless Firefox browser
    try:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            viewport={"width": 1366, "height": 768},
            locale="it-IT",
            geolocation={"latitude": 41.9028, "longitude": 12.4964},  # Rome, Italy
            permissions=["geolocation", "notifications"],
            timezone_id="Europe/Rome",
        )

        # Remove automation-related properties
        context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """
        )

        page = context.new_page()

    except Exception as e:
        print(f"Error in Step 1 (Browser Launch): {e}")
        return None, None, None

    try:
        # Step 2: Navigate to idealista.it
        page.goto("https://www.idealista.it")
        time.sleep(random.randint(4, 8))  # Random delay

        # Step 3: Click the "Accetta e chiudi" button
        try:
            page.click("#didomi-notice-agree-button")
            time.sleep(random.randint(4, 8))
        except Exception as e:
            print(f"Error in Step 3 (Accept Cookies): {e}")

        # Step 4-8: Perform login
        try:
            page.click("a[data-markup='header-login']")
            time.sleep(random.randint(4, 8))
            page.fill("input[name='email']", "retaggi1990@gmail.com")
            time.sleep(random.randint(4, 8))
            page.click("button[data-testid='text-button-test']:has-text('Continua')")
            time.sleep(random.randint(4, 8))
            page.fill("input[type='password']", "Diocane04")
            time.sleep(random.randint(4, 8))
            page.click("button[data-testid='text-button-test']:has-text('Accedi')")
            time.sleep(random.randint(4, 8))
        except Exception as e:
            print(f"Error in Step 4-8 (Login): {e}")

        return browser, context, page  # Returning the open session

    except Exception as e:
        print(f"Error in Step 2-8 (Initial Navigation and Login): {e}")
        browser.close()
        return None, None, None


def visit_extracted_links(browser, context, page, links_list, save_folder='visited_html'):
    """
    Visits extracted links using an already opened browser session.
    
    Args:
        browser: Playwright browser instance
        context: Playwright browser context
        page: Playwright page instance
        links_list: List of links to visit
        save_folder: Folder to save visited pages
    """
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    if not browser or not context or not page:
        print("Browser session is not active.")
        return

    for link in links_list:
        try:
            print(f"Visiting {link}")
            page.goto(link)
            time.sleep(random.randint(4, 8))  # Random delay

            # Save the page HTML to a JSON file
            html_content = page.content()
            link_id = link.rstrip("/").split("/")[-1]  # Extract unique ID from URL
            file_name = os.path.join(save_folder, f"{link_id}.json")

            with open(file_name, "w", encoding="utf-8") as file:
                json.dump({"url": link, "html": html_content}, file, ensure_ascii=False, indent=4)
            
            print(f"Saved HTML for {link} to {file_name}")

        except Exception as e:
            print(f"Error visiting {link}: {e}")

    # Step 14: Close the browser after visiting all links
    try:
        browser.close()
    except Exception as e:
        print(f"Error in Step 14 (Browser Close): {e}")
                

def extract_links_from_json(folder_name):
    """
    Extracts links of houses from all .json files in the specified folder.

    Args:
        folder_name (str): The name of the folder containing .json files.

    Returns:
        list: A list of extracted links.
    """
    links = []

    # Step 1: Ensure the folder exists
    if not os.path.exists(folder_name):
        print(f"Folder '{folder_name}' does not exist.")
        return links

    # Step 2: Iterate through all .json files in the folder
    for file_name in os.listdir(folder_name):
        if file_name.endswith(".json"):
            file_path = os.path.join(folder_name, file_name)
            try:
                # Step 3: Open and parse the JSON file
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    html_content = data.get("html", "")

                    # Step 4: Parse the HTML content with BeautifulSoup
                    soup = BeautifulSoup(html_content, "html.parser")

                    # Step 5: Extract links of houses
                    for a_tag in soup.find_all('a', href=True):
                        relative_url = a_tag.get('href')
                        if relative_url.startswith('/immobile/'):
                            full_url = "https://www.idealista.it" + relative_url
                            links.append(full_url)

            except Exception as e:
                print(f"Error processing file '{file_name}': {e}")

    return links
 
 
data_list = [
    ['busto-arsizio',"varese",'affitto'], 
    ['gallarate',"varese",'affitto'], 
    ['castellanza',"varese",'affitto'],
    ['lonate-pozzolo',"varese",'affitto'], 
    ['samarate',"varese",'affitto'], 
    ['cardano-al-campo',"varese",'affitto'], 
    ['varese',"varese",'affitto'], 
    ['pavia',"varese",'affitto'], 
    ['sondrio',"provincia",'affitto'], 
    ['trento',"provincia",'affitto'], 
    ['bolzano-bozen"',"provincia",'affitto']] 
save_folder='visited_html'  
name_dump = 'debug.json'
houses = []

if 1 :         
    browser, context, page = fetch_html_from_pagination(data_list)
    name_link = 'links.json'
    links_list = extract_links_from_json('download_html')
    with open(f"{name_link}", 'w', encoding='utf-8') as file:
            json.dump(links_list, file, indent=4, ensure_ascii=False)
            
         
    visit_extracted_links(browser,context,page,links_list,save_folder)

# Iterate through all JSON files in the folder
for file_name in os.listdir(save_folder):   
    file_path = os.path.join(save_folder, file_name)    
    try:
        # Pass the JSON file to the function
        houses.append(extract_house_details(file_path))
        print(f"Processed {file_name}")
    except Exception as e:
        print(f"Error processing file '{file_name}': {e}")
        
with open(f"{name_dump}", 'w', encoding='utf-8') as file:
        json.dump(houses, file, indent=4, ensure_ascii=False)

#Debug
if 1:
    import_json_to_sqlite(name_dump,'house.db')