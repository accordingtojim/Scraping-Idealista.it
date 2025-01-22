from scraping import  extract_auction_links_from_page_comune,extract_auction_links_from_page_provincia, extract_house_details,extract_ids_from_links
import json
from import_sqlite import import_json_to_sqlite
import argparse  # Aggiunto argparse
import os
from bs4 import BeautifulSoup
from undetected_multi import fetch_html_from_links,parallel_fetch_html
#from sqlite_import import import_json_to_sqlite
#from analyzing_pdf import custom_data_extraction,consolidate_json

houses = []
enhanced_auctions = []
links = set()
save_directory = "downloads"
name_dump = 'debug.json'
name_link = 'links.json'
dir_base = "browser_profiles"

# Crea la directory se non esiste
if not os.path.exists(dir_base):
    os.makedirs(dir_base)
    print(f"Directory creata: {dir_base}")
else:
    print(f"Directory già esistente: {dir_base}")

base_profile_dir = os.path.abspath(dir_base) # Directory per gestire profili unici creati dallo script

links = [    "https://www.idealista.it/immobile/31716553/",
    "https://www.idealista.it/immobile/31310558/",
    "https://www.idealista.it/immobile/30501368/",
    "https://www.idealista.it/immobile/28606771/",
    "https://www.idealista.it/immobile/31034392/",
    "https://www.idealista.it/immobile/10378631/",
    "https://www.idealista.it/immobile/5696603/",
    "https://www.idealista.it/immobile/22916640/",
    "https://www.idealista.it/immobile/31436908/"]

# with open(name_link, 'r', encoding='utf-8') as file:
#         links = json.load(file)  
# ids = extract_ids_from_links(links)

batch_size = len(links) // 2  # Modifica in base al numero di worker desiderati
links_batches = [links[i:i + batch_size] for i in range(0, len(links), batch_size)]

if 1:
    parallel_fetch_html(links_batches, base_profile_dir=base_profile_dir, output_dir="download_html", max_workers=2)
   



    
