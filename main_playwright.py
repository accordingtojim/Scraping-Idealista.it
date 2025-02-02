#name file = main_playwright.py
import time
import random
import os
import json
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from import_sqlite import import_json_to_sqlite
from scraping import fetch_html_from_pagination,extract_links_from_json,visit_extracted_links,extract_house_details,login_to_idealista
from test_vpn import connect_vpn,check_vpn_status,disconnect_vpn

num_attempts = 0
max_attempts = 4

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
    ['bolzano-bozen',"provincia",'affitto']
    ]

save_folder='visited_html'  
name_dump = 'debug.json'
houses = []
name_link = 'links.json'
browser = None
vpn_active = False

if vpn_active:
    if check_vpn_status != None:
        disconnect_vpn()
    time.sleep(2)

    connect_vpn()
    time.sleep(1)
    check_vpn_status()


if 0 :
    
    browser, context, page = login_to_idealista()
    fetch_html_from_pagination(browser, context, page,data_list)
    links_list = extract_links_from_json('download_html')
    with open(f"{name_link}", 'w', encoding='utf-8') as file:
            json.dump(links_list, file, indent=4, ensure_ascii=False)
 
 
with open(f"{name_link}", "r", encoding="utf-8") as file:
    links_list = json.load(file)  # my_list is now a Python list (if JSON is an array)  
             
while links_list and num_attempts < max_attempts:
    if browser == None:
        browser1, context1, page1 = login_to_idealista()
        
    links_list = visit_extracted_links(browser1,context1,page1,links_list,save_folder)
    
    if  links_list :       
        num_attempts += 1
        print("Gotcha! By a Captcha!")
        browser.close()
        time.sleep(1)
        if vpn_active:
            disconnect_vpn()
            time.sleep(1)
            connect_vpn()  # Connects to a random country
            print("🔎 Checking VPN status...")


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