from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import json
import os

def fetch_html_from_links(links, output_dir="download_html"):
    # Configura le opzioni di Chrome
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Crea la directory di output
    os.makedirs(output_dir, exist_ok=True)

    # Avvia Chrome non rilevabile
    driver = uc.Chrome(options=options)

    try:
        # Step 1: Login a Idealista
        driver.get("https://www.idealista.it/")
        print("Aperta la homepage di Idealista.")
        time.sleep(5)

        # Gestisci il popup dei cookie
        try:
            accept_cookies_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            )
            accept_cookies_button.click()
            print("Popup dei cookie gestito.")
        except Exception as e:
            print("Nessun popup dei cookie trovato o errore:", e)

        # Gestisci il login
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-markup='header-login']"))
        )
        login_button.click()
        time.sleep(2)
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys("retaggi1990@gmail.com")
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Continua']"))
        )
        continue_button.click()
        time.sleep(2)
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='password' and @data-testid='input-test-id']"))
        )
        password_input.send_keys("Diocane04")
        access_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='text-button-test']//span[text()='Accedi']"))
        )
        access_button.click()
        time.sleep(5)
        print("Login completato.")

        # Step 2: Itera sui link e salva gli HTML
        for link in links:
            try:
                driver.get(link)
                print(f"Aperta la pagina: {link}")
                time.sleep(5)  # Attendi il caricamento della pagina

                # Scorri fino alla sezione "Statistiche" (se necessario)
                try:
                    stats_section = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "stats"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", stats_section)
                    print("Scorrimento alla sezione 'Statistiche' completato.")
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

















