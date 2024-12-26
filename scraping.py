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

def fetch_html_with_cookies(url, headers=None, proxies=None):
    """
    Scarica il contenuto HTML di una pagina specificata dall'URL.

    :param url: URL della pagina da scaricare.
    :param headers: Dizionario con gli headers da usare nella richiesta (opzionale).
    :param proxies: Dizionario con i proxy da usare nella richiesta (opzionale).
    :return: Contenuto HTML della pagina o None in caso di errore.
    """
    # Headers di default (se non specificati)
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    # Usa gli headers forniti o quelli di default
    headers = headers or default_headers

    try:
        session = requests.Session()  # Usa una sessione persistente
        response = session.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()  # Solleva eccezioni per errori HTTP
        return response.text
    except RequestException as e:
        print(f"Errore durante il fetch: {e}")
        return None

def extract_auction_links_from_page(città, provincia, max_pagina='all', categoria="affitto"):
    links = set()  # Usiamo un set per evitare duplicati
    website_url = f"https://www.idealista.it/{categoria}-case/{città}-{provincia}/?ordine=pubblicazione-desc"
    print(f"Scaricando: {website_url}")
    
    # Scarica l'HTML
    html_content = fetch_html_with_cookies(website_url)
    if html_content is None:
        print(f"⚠️ Contenuto HTML vuoto")
        return links
    
    # Esporta il contenuto HTML in un file JSON di debug
    # debug_data = {
    #     "url": website_url,
    #     "html_content": html_content
    # }
    # with open("debug_html.json", "w", encoding="utf-8") as file:
    #     json.dump(debug_data, file, ensure_ascii=False, indent=4)
    # print("✅ Contenuto HTML esportato in debug_html.json")

    # Analizza il contenuto HTML con BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    for a_tag in soup.find_all('a', href=True):
        relative_url = a_tag.get('href')
        if relative_url.startswith('/immobile/'):
            # Costruisci l'URL completo
            full_url = "https://www.idealista.it" + relative_url
            links.add(full_url)
    
    return links

def extract_house_details(url, save_directory='downloads'):
    html_content = fetch_html_with_cookies(url)  # Funzione di recupero HTML da definire
    soup = BeautifulSoup(html_content, 'html.parser')

    # Trova l'elemento che contiene la sezione "Posizione"
    position_section = soup.find('div', id='headerMap')

    # Dividi la stringa sulla base del carattere '/'
    id_casa = url.split('/')[-2]  # L'ID si trova prima dell'ultimo '/'
    indirizzo = 'Indirizzo non trovato'
    zona = 'Zona non trovata'
    comune = 'Comune non trovato'
    area = 'Area non trovata'

    if position_section:
        indirizzo_element = position_section.find('ul')
        if indirizzo_element:
            indirizzo_list = indirizzo_element.find_all('li', class_='header-map-list')
            if len(indirizzo_list) > 3:
                indirizzo = indirizzo_list[0].text.strip()  # Indirizzo
                zona = indirizzo_list[1].text.strip()  # Zona Centro
                comune = indirizzo_list[2].text.strip()  # Busto Arsizio
                area = indirizzo_list[3].text.strip()  # Area Busto Arsizio-Castellanza, Varese
            else :
                #indirizzo = indirizzo_list[0].text.strip()  # Indirizzo
                zona = indirizzo_list[0].text.strip()  # Zona Centro
                comune = indirizzo_list[1].text.strip()  # Busto Arsizio
                area = indirizzo_list[2].text.strip()  # Area Busto Arsizio-Castellanza, Varese
                

    directory_path = f"asta_{indirizzo.replace('-', '').replace('  ', ' ').replace(' ', '_')}_{comune.replace('-', '').replace('  ', ' ').replace(' ', '_')}"
    details = {
        'Indirizzo': indirizzo,
        'Zona': zona,
        'Comune': comune,
        'Area': area,
        'Url' : url,
        'Id_casa': id_casa,
        'Directory': os.path.join(save_directory, directory_path)
    }

    return details


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


        


        
        

