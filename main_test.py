from scraping import  extract_auction_links_from_page, extract_house_details
import json
from import_sqlite import import_json_to_sqlite
import argparse  # Aggiunto argparse
import os
from bs4 import BeautifulSoup
#from sqlite_import import import_json_to_sqlite
#from analyzing_pdf import custom_data_extraction,consolidate_json

houses = []
enhanced_auctions = []
links = set()
save_directory = "downloads"
name_dump = 'debug.json'

lista_comune = ["busto-arsizio","castellanza","gallarate","samarate"]
lista_provincia = ["varese","varese","varese","varese"]
len_comune = len(lista_comune)
if 0 :
    for element in range(0,len_comune):
        nuovi_link = extract_auction_links_from_page(lista_comune[element], lista_provincia[element])
        links.update(nuovi_link)

links = extract_auction_links_from_page('varese')
for link in links: houses.append(extract_house_details(link))

#Debug
with open(f"{name_dump}", 'w', encoding='utf-8') as file:
    json.dump(houses, file, indent=4, ensure_ascii=False)

import_json_to_sqlite(name_dump,'house.db')

    
