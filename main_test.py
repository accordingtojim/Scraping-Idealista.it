from scraping import  extract_auction_links_from_page, extract_house_details,extract_ids_from_links
import json
from import_sqlite import import_json_to_sqlite
import argparse  # Aggiunto argparse
import os
from bs4 import BeautifulSoup
from undetc_test import fetch_html_from_links
#from sqlite_import import import_json_to_sqlite
#from analyzing_pdf import custom_data_extraction,consolidate_json

houses = []
enhanced_auctions = []
links = set()
save_directory = "downloads"
name_dump = 'debug.json'
name_link = 'links.json'

lista_comune = ["busto-arsizio"]
lista_provincia = ["varese"]
len_comune = len(lista_comune)
if 0 :
    for element in range(0,len_comune):
        nuovi_link = extract_auction_links_from_page(lista_comune[element], lista_provincia[element],'affitto',1)
        links.update(nuovi_link)
    links_list = list(links)
    with open(f"{name_link}", 'w', encoding='utf-8') as file:
            json.dump(links_list, file, indent=4, ensure_ascii=False)

with open(name_link, 'r', encoding='utf-8') as file:
        links = json.load(file)  
ids = extract_ids_from_links(links)

if 0:
    fetch_html_from_links(links, save_directory)
   
for id in ids:
    houses.append(extract_house_details(f"{save_directory}."+str(id)))
with open(f"{name_dump}", 'w', encoding='utf-8') as file:
        json.dump(houses, file, indent=4, ensure_ascii=False)

#Debug
if 0:
    

    import_json_to_sqlite(name_dump,'house.db')

    
