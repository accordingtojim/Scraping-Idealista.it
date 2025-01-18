from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import random
import json
import os
from concurrent.futures import ThreadPoolExecutor


def fetch_html_from_links(links, output_dir="download_html", profile_dir=None):
    # Configura le opzioni di Chrome
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")


    # Usa un profilo unico se specificato
    if profile_dir:
        print(f"Usando profilo unico: {profile_dir}")
        os.makedirs(profile_dir, exist_ok=True)
        options.add_argument(f"--user-data-dir={profile_dir}")

    # Crea la directory di output
    os.makedirs(output_dir, exist_ok=True)

    # Avvia Chrome non rilevabile
    driver = uc.Chrome(options=options)
    time.sleep(5)
    try:
        # Step 1: Apri la homepage di Idealista
        driver.get("https://www.idealista.it/")
        print("Aperta la homepage di Idealista.")
        time.sleep(random.uniform(5, 10))

        # Step 2: Gestisci il popup dei cookie
        try:
            # Step 2: Gestisci il popup dei cookie
            accept_cookies_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            )
            accept_cookies_button.click()
            print("Popup dei cookie gestito.")
            time.sleep(random.uniform(5, 10))

            # Step 3: Gestisci il popup di Google Translate
            try:
                time.sleep(random.uniform(2, 5))
                ActionChains(driver).move_by_offset(10, 10).click().perform()
                print("Popup di Google Translate chiuso.")
            except Exception as e:
                print("Errore nel chiudere il popup di Google Translate:", e)

            # Step 4: Trova e clicca sul pulsante "Accedi"
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-markup='header-login']"))
            )
            login_button.click()
            print("Cliccato sul pulsante Accedi.")
            time.sleep(random.uniform(5, 10))

            # Step 5: Inserisci l'email nel campo "email"
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_input.send_keys("retaggi1990@gmail.com")
            print("Email inserita.")

            # Step 6: Clicca sul pulsante "Continua"
            continue_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Continua']"))
            )
            continue_button.click()
            print("Cliccato su Continua.")
            time.sleep(random.uniform(5, 10))

            # Step 7: Inserisci la password
            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password' and @data-testid='input-test-id']"))
            )
            password_input.clear()
            password_input.send_keys("Diocane04")
            print("Password inserita.")

            # Step 8: Clicca sul pulsante "Accedi"
            access_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='text-button-test']//span[text()='Accedi']"))
            )
            access_button.click()
            print("Cliccato su Accedi.")
            time.sleep(random.uniform(5, 10))

        except Exception as e:
            print(f"Errore o popup non trovato: {e}")

        # Step 9: Itera sui link e salva gli HTML
        for link in links:
            try:
                # Apri il link desiderato
                driver.get(link)
                print(f"Aperta la pagina: {link}")
                time.sleep(random.uniform(10, 15))  # Attendi il caricamento della pagina

                # Scorri fino alla sezione "Statistiche" (se necessario)
                try:
                    stats_section = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "stats"))
                    )
                    for i in range(0, 2000, 200):  # Scorrimento graduale
                        driver.execute_script(f"window.scrollBy(0, {i});")
                        time.sleep(random.uniform(0.5, 1.5))
                    driver.execute_script("arguments[0].scrollIntoView(true);", stats_section)
                    print("Scorrimento alla sezione 'Statistiche' completato.")
                    time.sleep(random.uniform(8, 13))  # Attendi il caricamento delle informazioni
                except Exception:
                    print("Sezione 'Statistiche' non trovata, continuo.")

                # Salva l'HTML in un file JSON
                html_content = driver.page_source
                output_file = os.path.join(output_dir, f"{link.split('/')[-2]}.json")
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump({"url": link, "html": html_content}, f, ensure_ascii=False, indent=4)
                print(f"HTML salvato in: {output_file}")
            except Exception as e:
                print(f"Errore con il link {link}: {e}")

    except Exception as e:
        print(f"Errore durante l'esecuzione: {e}")
    finally:
        driver.quit()

def parallel_fetch_html(links_batches, base_profile_dir, output_dir="download_html", max_workers=2):
    """
    Esegue il fetch in parallelo suddividendo i link in batch e utilizzando profili unici per Chrome.
    """
    os.makedirs(base_profile_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    def run_batch(links, profile_suffix):
        profile_dir = os.path.join(base_profile_dir, f"profile_{profile_suffix}")
        print(f"Avviando batch {profile_suffix} con {len(links)} link.")
        fetch_html_from_links(links, output_dir, profile_dir)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, links in enumerate(links_batches):
            executor.submit(run_batch, links, i)




















