from scraping import  extract_auction_links_from_page, extract_house_details
import json
import argparse  # Aggiunto argparse
import os
from bs4 import BeautifulSoup
#from sqlite_import import import_json_to_sqlite
#from analyzing_pdf import custom_data_extraction,consolidate_json

houses = []
enhanced_auctions = []
save_directory = "downloads"
name_dump = 'debug.json'

links = extract_auction_links_from_page("busto-arsizio","varese")
for link in links: houses.append(extract_house_details(link))

#Debug
with open(f"{name_dump}", 'w', encoding='utf-8') as file:
    json.dump(houses, file, indent=4, ensure_ascii=False)


    
