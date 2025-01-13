from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time

def login_and_fetch_with_selenium():
    # Configura le opzioni di Chrome
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Avvia Chrome non rilevabile
    driver = uc.Chrome(options=options)

    try:
        # Step 1: Apri la homepage di Idealista
        driver.get("https://www.idealista.it/")
        print("Aperta la homepage di Idealista.")
        time.sleep(5)

        # Step 2: Gestisci il popup dei cookie
        try:
            accept_cookies_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
            )
            accept_cookies_button.click()
            print("Popup dei cookie gestito.")
            time.sleep(5)
        except Exception as e:
            print("Nessun popup dei cookie trovato o errore:", e)

        # Step 3: Gestisci il popup di Google Translate
        try:
            time.sleep(2)
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
        time.sleep(5)

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
        time.sleep(5)

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
        time.sleep(5)

        # Step 9: Naviga al link desiderato
        url_to_fetch = "https://www.idealista.it/immobile/31598210/"
        driver.get(url_to_fetch)
        print(f"Aperta la pagina: {url_to_fetch}")

        # Step 10: Scroll fino alla sezione "Statistiche" e attendi
        stats_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "stats"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", stats_section)  # Scroll fino alla sezione
        print("Scorrimento alla sezione 'Statistiche' completato.")
        time.sleep(10)  # Attendi 10 secondi per il caricamento delle informazioni

        # Step 11: Salva il contenuto della pagina
        with open("pagina_ottenuta.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Contenuto salvato in 'pagina_ottenuta.html'.")

    except Exception as e:
        print(f"Errore: {e}")
    finally:
        driver.quit()

# Esegui lo script
login_and_fetch_with_selenium()













