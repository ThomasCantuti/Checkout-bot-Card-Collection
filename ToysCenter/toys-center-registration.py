from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import string
import random
import time
import json
import logging
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Utility.utils import captcha_solver_cloudflare, cookie_accept

load_dotenv()

TC_REGISTRATION_URL = os.environ.get('TC_REGISTRATION_URL')
TOYS_CENTER_KEY = os.environ.get('TOYS_CENTER_KEY')
ROOT_PATH = os.environ.get('ROOT_PATH')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("ToysCenter-Bot")

USER_PATH = os.path.join(ROOT_PATH, "Data", "alle.json")
USER_DATA = json.load(open(USER_PATH))


# ==========================
# Funzione principale
# ==========================

def main():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    driver.implicitly_wait(10)

    try:
        create_new_account(driver)
        
        print("Registrazione completata!")

    except Exception as e:
        print(f"Si è verificato un errore: {e}")
    finally:
        # Chiude il browser alla fine
        time.sleep(5)  # per debug, poi puoi togliere o abbassare il tempo
        driver.quit()

# ==========================
# Creazione nuovo account
# ==========================
def create_new_account(driver):
    """
    Visita la pagina del profilo
    Completare la registrazione
    """
    driver.get(TC_REGISTRATION_URL)
    
    # Accettazione cookie
    cookie_accept(driver)
    
    # Captcha
    captcha_solver_cloudflare(driver, TC_REGISTRATION_URL, TOYS_CENTER_KEY)
    time.sleep(10)
    
    # Verifica se ci sono altri overlay o elementi da gestire
    try:
        overlays = driver.find_elements(By.CSS_SELECTOR, ".tw-mx-auto.tw-text-center")
        for overlay in overlays:
            if overlay.is_displayed():
                logger.info("Trovato overlay che potrebbe interferire, tento di rimuoverlo")
                driver.execute_script("arguments[0].remove();", overlay)
    except Exception as e:
        logger.warning(f"Tentativo di rimozione overlay fallito: {str(e)[:100]}")

    # Compilazione form
    logger.info("Inizio compilazione form")
    driver.find_element(By.XPATH, '//*[@id="customer_name"]').send_keys(USER_DATA["nome"])
    driver.find_element(By.XPATH, '//*[@id="customer_surname"]').send_keys(USER_DATA["cognome"])
    date_input = driver.find_element(By.ID, "customer_birthday")
    date_input.clear()
    date_input.send_keys(USER_DATA["data_nascita"])
    date_input.send_keys(Keys.TAB)
    dropdown = driver.find_element(By.CSS_SELECTOR, ".choices__inner")
    dropdown.click()
    time.sleep(1)
    option = driver.find_element(By.CSS_SELECTOR, f"div[data-value='{USER_DATA['sesso']}']")
    option.click()
    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(USER_DATA["email"])
    driver.find_element(By.XPATH, '//*[@id="email_confirm"]').send_keys(USER_DATA["email"])
    driver.find_element(By.XPATH, '//*[@id="customer_phone_"]').send_keys(USER_DATA["telefono"])
    USER_DATA["password"] = genera_password_sicura(USER_DATA)
    json.dump(USER_DATA, open(USER_PATH, "w"), indent=4)
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(USER_DATA["password"])
    driver.find_element(By.XPATH, '//*[@id="password_confirm"]').send_keys(USER_DATA["password"])
    
    time.sleep(5)

    # Accettazione privacy
    toggle_checkbox = driver.find_element(By.NAME, "gdpr_privacy")
    driver.execute_script("arguments[0].click();", toggle_checkbox)
    
    time.sleep(5)
    
    driver.find_element(By.XPATH, '//*[@id="content"]/div/div/form/div/div[5]/button').click()
    
    '''# Wait for the submit button to be enabled
    WebDriverWait(driver, 10).until(lambda d: d.find_element(By.CSS_SELECTOR, 'form button[type="submit"]').is_enabled())
    # Click the submit button
    driver.find_element(By.CSS_SELECTOR, 'form button[type="submit"]').click()'''
    
    time.sleep(5)
    
def genera_password_sicura(dati_utente, lunghezza=12):
    """
    Genera una password sicura, la inserisce nel dict `dati_utente` con chiave 'password'
    e la restituisce come stringa.
    
    :param dati_utente: dict già esistente nel quale aggiungere la password
    :param lunghezza: lunghezza desiderata della password (default: 12)
    :return: la password generata come stringa
    """
    # Definiamo i caratteri utilizzabili: 
    # lettere maiuscole, minuscole, cifre e simboli
    caratteri_validi = (
        string.ascii_lowercase + 
        string.ascii_uppercase + 
        string.digits + 
        "!@#$%^&*()-_=+<>?"  # Puoi modificare i simboli se preferisci
    )
    
    # Creiamo la password come lista di caratteri casuali
    password_generata = [
        random.choice(caratteri_validi) for _ in range(lunghezza)
    ]
    
    # Convertila in stringa
    password_finale = "".join(password_generata)
    
    # Salviamo la password nel dict
    dati_utente["password"] = password_finale
    
    return password_finale

# ==========================
# Avvio script
# ==========================
if __name__ == "__main__":
    main()