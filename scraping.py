import time
import random
import os
import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import asyncio

def login_to_idealista():
    
    """
    Logs into Idealista and returns an open browser session.
    
    Returns:
        browser (Playwright browser instance)
        context (Playwright browser context)
        page (Playwright page instance)
    """
    p = sync_playwright().start()
    try:
        browser = p.firefox.launch(headless=False, args=["--start-fullscreen"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            viewport={"width": 1780, "height": 880},
            locale="it-IT",
            geolocation={"latitude": 41.9028, "longitude": 12.4964},
            permissions=["geolocation", "notifications"],
            timezone_id="Europe/Rome",
        )
        
        # Remove automation-related properties
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.navigator.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'languages', {get: () => ['it-IT', 'en-US']});
            Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
            Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
            Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4});
        """)
        
        page = context.new_page()
        
        page.goto("https://www.idealista.it")
        time.sleep(random.uniform(4, 8))
        
        try:
            page.click("#didomi-notice-agree-button")
            time.sleep(random.randint(4, 8))
        except Exception as e:
            print(f"Error in Step 3 (Accept Cookies): {e}")
        
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
        
        return browser, context, page
    except Exception as e:
        print(f"Error in Step 1 (Browser Launch): {e}")
        return None, None, None
def fetch_html_from_pagination(browser, context, page, data_list, download_html='download_html'):
    """
    Fetches paginated HTML content from Idealista using an existing browser session.
    """
    if not os.path.exists(download_html):
        os.makedirs(download_html)

    try:
        for città, provincia, categoria in data_list:
            try:
                base_url = f"https://www.idealista.it/{categoria}-case/{città}-{provincia}/"
                page.goto(base_url)
                time.sleep(random.randint(4, 8))

                html_content = page.content()
                soup = BeautifulSoup(html_content, "html.parser")
                pagination = soup.find("div", class_="pagination")
                if pagination:
                    page_numbers = [
                        int(link.text)
                        for link in pagination.find_all("a")
                        if link.text.isdigit()
                    ]
                    number_of_pages = max(page_numbers) if page_numbers else 1
                else:
                    number_of_pages = 1

                print(f"Number of pages found for {base_url}: {number_of_pages}")

                first_page_file = os.path.join(download_html, f"{città}_{provincia}_page_1.json")
                with open(first_page_file, "w", encoding="utf-8") as file:
                    json.dump({"url": base_url, "html": html_content}, file, ensure_ascii=False, indent=4)
                print(f"Saved HTML for {base_url} to {first_page_file}")

                for page_num in range(2, number_of_pages + 1):
                    next_page_url = f"{base_url}lista-{page_num}.htm"
                    print(f"Visiting {next_page_url}")
                    try:
                        page.goto(next_page_url)
                        time.sleep(random.randint(4, 8))

                        html_content = page.content()
                        file_name = os.path.join(download_html, f"{città}_{provincia}_page_{page_num}.json")
                        with open(file_name, "w", encoding="utf-8") as file:
                            json.dump({"url": next_page_url, "html": html_content}, file, ensure_ascii=False, indent=4)
                        print(f"Saved HTML for {next_page_url} to {file_name}")
                    except Exception as e:
                        print(f"Error in Step 13 (Page {page_num} Fetch for {base_url}): {e}")
            except Exception as e:
                print(f"Error processing {città}, {provincia}, {categoria}: {e}")

    except Exception as e:
        print(f"Error in Step 2-8 (Fetching HTML): {e}")
        browser.close()
        return None

    return True

def is_captcha_page(html_content):
    """
    Determines if the page contains a Captcha challenge based on its HTML structure.
    """
    captcha_keywords = [
        'geo.captcha-delivery.com',  # DataDome Captcha URL
        'DataDome CAPTCHA',  # Captcha iframe title
        'c.js',  # DataDome script
        'var dd=',  # Captcha-related script
        '<iframe',  # If there's an unexpected iframe, might be Captcha
        'allow-scripts allow-same-origin allow-forms',  # Common Captcha sandbox settings
    ]
    return len(html_content) < 5000 #any(keyword in html_content.lower() for keyword in captcha_keywords) or 

import os
import time
import random
import json
from playwright.sync_api import sync_playwright

def visit_extracted_links(browser=None, context=None, page=None, links_list=[], save_folder='visited_html'):
    """
    Visits extracted links using an already opened browser session, scrolls up/down,
    and ensures each page is fully loaded before moving to the next.
    
    Args:
        browser: Playwright browser instance
        context: Playwright browser context
        page: Playwright page instance
        save_folder: Folder to save visited pages
    """
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
            
    successfully_links_reached = []
    exception = 0
    for link in links_list[:]:  # Iterate over a copy to allow modification
        try:
            print(f"🔗 Visiting {link}")
            page.goto(link, timeout=60000)  # Increased timeout to ensure full load
            time.sleep(random.uniform(4, 8))  # Random delay to simulate human behavior

            # ✅ Scroll up and down randomly
            for _ in range(random.randint(1, 3)):  # Perform 2 to 4 random scroll actions
                scroll_distance = random.randint(300, 800)  # Scroll between 300px and 800px
                page.evaluate(f"window.scrollBy(0, {scroll_distance});")  # Scroll down
                time.sleep(random.uniform(1, 3))  # Pause briefly
                page.evaluate(f"window.scrollBy(0, {-scroll_distance // 2});")  # Scroll up slightly
                time.sleep(random.uniform(1, 3))  # Pause again
            
            # Ensure page is fully loaded before proceeding
            html_content = page.content()
            if not is_captcha_page(html_content):
                link_id = link.rstrip("/").split("/")[-1]  # Extract unique ID from URL
                file_name = os.path.join(save_folder, f"{link_id}.json")

                with open(file_name, "w", encoding="utf-8") as file:
                    json.dump({"url": link, "html": html_content}, file, ensure_ascii=False, indent=4)
                print(f"✅ Saved HTML for {link} to {file_name}")
                successfully_links_reached.append(link)  # Add to successful links list
                links_list.remove(link)  # Remove successfully processed link from the global list
                
            else:
                print(f"⚠️ Page did not load correctly or contains CAPTCHA for {link}, skipping...")
                browser.close()
                print("🛑 Browser session closed.")
                break

        except Exception as e:
            print(f"❌ Error visiting {link}: {e}")
            exception += 1
            if exception > 3:
                print("🛑 Too many exceptions, closing browser...")
                break
            continue  # Move to the next link even if one fails

    return links_list 
  
                
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

def extract_house_details(json_file_path):
    # Carica il file JSON
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Estrai i valori da JSON
    url = data.get('url', '')
    html_content = data.get('html', '')

    soup = BeautifulSoup(html_content, 'html.parser')
    directory_path = ''

    # Trova l'elemento che contiene la sezione "Posizione"
    position_section = soup.find('div', id='headerMap')

    # Dividi la stringa sulla base del carattere '/'
    id_casa = url.split('/')[-2]  # L'ID si trova prima dell'ultimo '/'
    indirizzo = 'Indirizzo non trovato'
    zona = 'Zona non trovata'
    comune = 'Comune non trovato'
    area = 'Area non trovata'
    list_indirizzo = ['Via', 'Corso', 'Piazza']

    if position_section:
        indirizzo_element = position_section.find('ul')
        if indirizzo_element:
            indirizzo_list = indirizzo_element.find_all('li', class_='header-map-list')
            if len(indirizzo_list) > 3:
                indirizzo = indirizzo_list[0].text.strip()  # Indirizzo
                zona = indirizzo_list[1].text.strip()  # Zona Centro
                comune = indirizzo_list[2].text.strip()  # Busto Arsizio
                area = indirizzo_list[3].text.strip()  # Area Busto Arsizio-Castellanza, Varese
            elif len(indirizzo_list) == 3:
                for i in list_indirizzo:
                    if i in indirizzo_list[0].text.strip():
                        indirizzo = indirizzo_list[0].text.strip()
                        comune = indirizzo_list[1].text.strip()  # Busto Arsizio
                        area = indirizzo_list[2].text.strip()  # Area Busto Arsizio-Castellanza, Varese
                        break
                    else:
                        zona = indirizzo_list[0].text.strip()  # Zona Centro
                        comune = indirizzo_list[1].text.strip()  # Busto Arsizio
                        area = indirizzo_list[2].text.strip()  # Area Busto Arsizio-Castellanza, Varese
            else:
                indirizzo = 'Indirizzo non trovato'
                zona = 'Zona non trovata'
                comune = 'Comune non trovato'
                area = 'Area non trovata'

    # Estrazione prezzo e prezzo al metro quadro
    prezzo = 'Prezzo non trovato'
    prezzo_mq = 'Prezzo al m² non trovato'

    price_section = soup.find('article', class_='price-feature')
    if price_section:
        price_details = price_section.find_all('p', class_='flex-feature')
        for detail in price_details:
            label = detail.find('span', class_='flex-feature-details')
            if not label:
                continue
            value = detail.find('strong', class_='flex-feature-details') or detail.find_all('span', class_='flex-feature-details')[-1]
            if label and value:
                if "Prezzo dell'immobile" in label.text:
                    prezzo = value.text.strip()
                elif 'Prezzo al m²' in label.text:
                    prezzo_mq = value.text.strip()

    try:
        prezzo_float = round(float(prezzo.replace('€/mese', '').replace('.', '').replace(',', '.').strip()))
        prezzo_mq_float = round(float(prezzo_mq.replace('€/m²', '').replace('.', '').replace(',', '.').strip()))
        mq_float = round(prezzo_float / prezzo_mq_float)
    except (ValueError, TypeError, ZeroDivisionError):
        # Se c'è un errore, assegna i valori originali o un fallback
        prezzo_float = prezzo if 'prezzo_float' not in locals() else prezzo_float
        prezzo_mq_float = prezzo_mq if 'prezzo_mq_float' not in locals() else prezzo_mq_float
        mq_float = None  # Nessun calcolo possibile


    # Estrazione statistiche
    stats_section = soup.find('div', id='stats-ondemand')
    visite = 'Visite non trovate'
    contatti_email = 'Contatti via email non trovati'
    salvato_preferito = 'Salvato come preferito non trovato'

    if stats_section:
        stats_list = stats_section.find_all('li')
        for stat in stats_list:
            if 'visite' in stat.text:
                visite = stat.find('strong').text.strip()
            elif 'contatti via email' in stat.text:
                contatti_email = stat.find('strong').text.strip()
            elif 'salvato come preferito' in stat.text:
                salvato_preferito = stat.find('strong').text.strip()

    directory_path = f"asta_{indirizzo.replace('-', '').replace('  ', ' ').replace(' ', '_')}_{comune.replace('-', '').replace('  ', ' ').replace(' ', '_')}"
    details = {
        'Indirizzo': indirizzo,
        'Zona': zona,
        'Comune': comune,
        'Area': area,
        'Prezzo': prezzo_float,
        'Prezzo al m²': prezzo_mq_float,
        'Superficie in mq': mq_float,
        'Url': url,
        'Id_casa': id_casa,
        'Visite': visite,
        'Contatti via email': contatti_email,
        'Salvato come preferito': salvato_preferito,
        #'Directory': os.path.join(save_directory, directory_path)
    }

    return details
