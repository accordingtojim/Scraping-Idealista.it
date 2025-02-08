import requests
import time
import random
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import mimetypes
import re
import tkinter as tk
from tkinter import messagebox
from requests.exceptions import RequestException
from playwright.sync_api import sync_playwright

# da riga 12 a 21 può essere anche sostituito semplicemente da do_download = 1
def ask_user():
    root = tk.Tk()
    root.withdraw()  # Nasconde la finestra principale
    # Mostra la finestra di dialogo con le opzioni 'Yes' e 'No'
    response = messagebox.askyesno("Conferma Download", "Vuoi eseguire i download?")
    # Se l'utente seleziona 'Yes', assegna 1 a do_download, altrimenti assegna 0
    do_download = 1 if response else 0
    return do_download

#do_download = ask_user()

def load_province_map(json_file_path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            province_map = json.load(file)
        return province_map
    except FileNotFoundError:
        print(f"Errore: il file {json_file_path} non è stato trovato.")
        return {}
    except json.JSONDecodeError:
        print(f"Errore: il file {json_file_path} non contiene un JSON valido.")
        return {}
    
# Funzione di supporto per pulire eventuale testo
def clean_number(value):
    if value:
        # Sostituisce la virgola con un punto per conversione in float
        value = value.replace(',', '.')
        return value
    return 1

# Funzione di supporto per pulire il campo "Offerta Minima" (rimuove il "(1)")
def clean_offerta_minima(value):
    if value:
        # Rimuove annotazioni come "(1)", "(2)", ecc.
        cleaned = re.sub(r'\(\d+\)', '', value).strip()  # Modificato per rimuovere numeri tra parentesi
        # Rimuove simboli monetari come '€'
        cleaned = re.sub(r'[^\d,\.]', '', cleaned).strip()  # Mantiene solo numeri, virgola e punto
        # Rimuove il punto come separatore delle migliaia
        cleaned = cleaned.replace('.', '')  # Rimuove il punto
        # Passa il risultato a clean_number per convertirlo in un numero
        return clean_number(cleaned)
    return 1


import random
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException

import time
import random
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException
def fetch_html_with_playwright(url):
    """
    Fetch the HTML content of a webpage using Playwright with a browser.

    :param url: URL of the webpage to fetch.
    :return: The HTML content as a string or None if an error occurs.
    """
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=False)  # Open Firefox browser
            context = browser.new_context()

            # Open a new page
            page = context.new_page()

            # Navigate to the URL
            print(f"Navigating to: {url}")
            page.goto(url, timeout=60000)

            # Wait for the page to load completely
            time.sleep(random.uniform(3, 5))

            # Get the HTML content
            html_content = page.content()

            # Close the browser
            browser.close()

            return html_content
    except Exception as e:
        print(f"⚠️ Error fetching page with Playwright: {e}")
        return None
    
def extract_auction_links_from_page_comune(città, provincia='provincia', categoria='affitto'):
    """
    Extracts listing links from all result pages for a given city and province and saves HTML files.

    :param città: City name.
    :param provincia: Province name.
    :param categoria: Search category (e.g., 'affitto').
    """
    base_url = f"https://www.idealista.it/{categoria}-case/{città}-{provincia}/"
    html_content = fetch_html_with_playwright(base_url)

    if not html_content:
        print("Failed to fetch the base URL.")
        return

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the maximum number of pages
    max_page = 1
    pagination = soup.find('ul')
    if pagination:
        for li in pagination.find_all('li'):
            if li.a and li.a.text.isdigit():
                max_page = max(max_page, int(li.a.text))

    print(f"Maximum number of pages: {max_page}")

    # Create the download directory
    os.makedirs('download_link', exist_ok=True)

    for page_number in range(1, max_page + 1):
        if page_number == 1:
            url = base_url
        else:
            url = f"{base_url}lista-{page_number}.htm"

        print(f"Fetching page {page_number}: {url}")
        html_content = fetch_html_with_playwright(url)

        if html_content:
            file_path = os.path.join('download_link', f'page_{page_number}.json')
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({'url': url, 'content': html_content}, f, ensure_ascii=False, indent=4)
            print(f"Page {page_number} saved to {file_path}.")
        else:
            print(f"Failed to fetch page {page_number}.")





def extract_auction_links_from_page_provincia(provincia='provincia', categoria='affitto', num_pagine='all'):
    """
    Estrae i link degli annunci da tutte le pagine dei risultati per una data città e provincia.
    
    :param città: Nome della città.
    :param provincia: Nome della provincia.
    :param categoria: Categoria di ricerca (es. 'affitto').
    :param num_pagine: Numero di pagine da scaricare (default 'all' per scaricare tutte).
    """
    base_url = f"https://www.idealista.it/{categoria}-case/{provincia}-provincia/"
    params = {'ordine': 'pubblicazione-desc'}
    links = set()
    page_number = 1

    while True:
        if num_pagine != 'all' and page_number > int(num_pagine):
            print(f"🔄 Numero massimo di pagine ({num_pagine}) raggiunto. Interruzione.")
            break

        if page_number == 1:
            url = base_url
        else:
            url = f"{base_url}lista-{page_number}.htm"

        print(f"Scaricando: {url}")
        html_content = fetch_html_with_cookies(url)
        if html_content is None:
            print(f"⚠️ Contenuto HTML vuoto per la pagina {page_number}. Interruzione.")
            break

        soup = BeautifulSoup(html_content, 'html.parser')

        # Estrai i link degli annunci
        page_links = 0
        for a_tag in soup.find_all('a', href=True):
            relative_url = a_tag.get('href')
            if relative_url.startswith('/immobile/'):
                full_url = "https://www.idealista.it" + relative_url
                if full_url not in links:
                    links.add(full_url)
                    page_links += 1

        if page_links == 0:
            print(f"⚠️ Nessun nuovo link trovato nella pagina {page_number}. Interruzione.")
            break

        page_number += 1
        time.sleep(1)  # Rispetta il server evitando richieste troppo ravvicinate

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


def extract_ids_from_links(links):
    """
    Estrae gli ID dai link forniti.

    :param links: Lista di link.
    :return: Lista di ID estratti dai link.
    """
    ids = []
    for link in links:
        try:
            # L'ID è il penultimo elemento separato da '/'
            id_immobile = link.strip('/').split('/')[-1]
            ids.append(id_immobile)
        except IndexError:
            print(f"⚠️ Link non valido: {link}")
    return ids


def download_files_from_page(url, auction_directory):
    """Scarica tutti i file da una pagina di un'asta in multithreading."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Errore durante il download della pagina: {e}")
        return
    
    soup = BeautifulSoup(html_content, 'html.parser')

    # Crea la directory specifica per l'asta se non esiste
    if not os.path.exists(auction_directory):
        os.makedirs(auction_directory)

    # Cerca i link ai file nel nuovo formato HTML
    document_container = soup.find('ul', class_='documenti d-flex flex-wrap')
    if not document_container:
        print("Nessun documento trovato nella pagina.")
        return
    
    links = document_container.find_all('a', href=True)
    
    with ThreadPoolExecutor(max_workers=2) as executor:  # Puoi modificare max_workers per regolare il grado di parallelismo
        futures = []
        for link in links:
            href = link['href']
            link_text = link.text.lower()
            if any(keyword in link_text for keyword in ["planimetria", "ordinanza", "perizia", "avviso"]):
                file_name = href.split('/')[-1]
                file_url = href if href.startswith('http') else "https://documents.astalegale.net" + href
                file_path = os.path.join(auction_directory, file_name)

                # Funzione diretta per il download
                futures.append(
                    executor.submit(
                        lambda url, path: 
                        download_file(url, path), 
                        file_url, 
                        file_path
                    )
                )

        for future in as_completed(futures):
            try:
                future.result()  # Controlla eventuali eccezioni nel thread
            except Exception as e:
                print(f"Errore durante il download di un file: {e}")

def download_file(file_url, file_path):
    """Scarica e salva un singolo file, aggiunge l'estensione se mancante e gestisce la rimozione di duplicati."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        session = requests.Session()  # Usa una sessione persistente
        print(f"Scaricando {file_path} da: {file_url}")
        
        file_response = session.get(file_url, headers=headers, stream=True)
        file_response.raise_for_status()
        
        # Ottieni il content-type e determina l'estensione
        content_type = file_response.headers.get('Content-Type', '')
        guessed_extension = mimetypes.guess_extension(content_type)
        
        # Se il file_path non ha un'estensione, usiamo quella rilevata
        if '.' not in os.path.basename(file_path) and guessed_extension:
            file_path_with_extension = file_path + guessed_extension
        elif not file_path.endswith(('.pdf', '.jpg', '.png', '.docx', '.xlsx')) and guessed_extension:
            file_path_with_extension = file_path + guessed_extension
        else:
            file_path_with_extension = file_path
        
        # Se il file con estensione esiste, non lo scarichiamo di nuovo
        if os.path.exists(file_path_with_extension):
            print(f"❌ File già esistente: {file_path_with_extension}, download saltato.")
            return

        with open(file_path_with_extension, 'wb') as file:
            for chunk in file_response.iter_content(chunk_size=1024):
                file.write(chunk)
        
        print(f"✅ File salvato in: {file_path_with_extension}")
        
        # Elimina il file senza estensione se esiste
        if file_path != file_path_with_extension and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️ File duplicato rimosso: {file_path}")
            except Exception as e:
                print(f"⚠️ Errore durante la rimozione del file duplicato {file_path}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore durante il download del file {file_path}: {e}")

def download_files_for_all_auctions(auction, save_directory="downloads"):
    """Scarica i file per tutte le aste, eseguendo il download delle pagine e dei file in multithreading."""
    indirizzo = auction['Indirizzo']
    comune = auction['Comune']
    auction_url = auction['URL']
    directory_name = f"{indirizzo}_{comune}" if indirizzo != 'Indirizzo non trovato' else "asta_generica"
    auction.update({'Directory_name': directory_name})
    auction_directory = os.path.join(save_directory, directory_name)

    asteannuncio_url = auction_url.replace("www.canaleaste.it", "www.asteannunci.it")
    print(f"Scaricando i file per l'asta: {asteannuncio_url}")

    download_files_from_page(asteannuncio_url, auction_directory)


        


        
        

