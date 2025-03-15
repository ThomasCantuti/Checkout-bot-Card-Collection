from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import string
import random
import time
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("ToysCenter-Bot")

PRODUCT_URL = "https://www.toyscenter.it/my-account/"
USER_PATH = "alle.json"
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
    driver.get(PRODUCT_URL)
    create_account_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div/div[3]/div[2]/a'))
    )
    create_account_button.click()
    
    # Accettazione cookie
    try:
        cookie_accept_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")  
        cookie_accept_btn.click()
        # attendo un istante che il banner scompaia
        time.sleep(1)
    except:
        # se non lo trova, magari è già chiuso, ignora
        pass
    
    # Captcha
    handle_cloudflare_captcha(driver)
    time.sleep(5)
    
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

    # Accettazione privacy
    toggle_checkbox = driver.find_element(By.NAME, "gdpr_privacy")
    driver.execute_script("arguments[0].click();", toggle_checkbox)
    
    # Click su "Creare account" con diverse strategie
    try:
        # Prima strategia: Scroll e click standard
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div/form/div/div[5]/button'))
        )
        submit_button.click()
        logger.info("Pulsante 'Creare account' cliccato con successo")
    except Exception as e:
        logger.warning(f"Click standard fallito: {str(e)[:100]}")
        
        try:
            # Seconda strategia: JavaScript
            submit_button = driver.find_element(By.XPATH, '//*[@id="content"]/div/div/form/div/div[5]/button')
            driver.execute_script("arguments[0].click();", submit_button)
            logger.info("Pulsante 'Creare account' cliccato via JavaScript")
        except Exception as e:
            logger.warning(f"Click JavaScript fallito: {str(e)[:100]}")
            
            try:
                # Terza strategia: Submit del form
                form = driver.find_element(By.TAG_NAME, "form")
                driver.execute_script("arguments[0].submit();", form)
                logger.info("Form inviato direttamente via submit")
            except Exception as e:
                logger.error(f"Impossibile inviare il form: {str(e)[:100]}")
                raise
    
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

def handle_cloudflare_captcha(driver) -> None:
    """Gestisce il CAPTCHA di CloudFlare se presente."""
    try:
        # Cerca elementi con ID che inizia con cf-chl-widget
        elements = driver.find_elements(By.XPATH, "//*[starts-with(@id, 'cf-chl-widget')]")
        if elements:
            cf_element = elements[0]
            full_id = cf_element.get_attribute('id')
            base_id = full_id.replace("_response", "") if "_response" in full_id else full_id
            logger.info(f"Trovato elemento CloudFlare captcha con ID: {base_id}")
            
            # Utilizza JavaScript avanzato con il base_id estratto
            try:
                js_result = driver.execute_script(f"""
                    // Verifico se esiste l'elemento con ID completo
                    var element = document.getElementById('{full_id}');
                    if (element) {{
                        console.log('Trovato elemento con ID completo: {full_id}');
                        element.click();
                        return true;
                    }}
                    
                    // Provo con ID base (senza _response)
                    element = document.getElementById('{base_id}');
                    if (element) {{
                        console.log('Trovato elemento con ID base: {base_id}');
                        element.click();
                        return true;
                    }}
                    
                    // Provo con XPath specifico per il base_id
                    element = document.evaluate("//*[@id='{base_id}']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (element) {{
                        console.log('Trovato elemento con XPath basato su ID: {base_id}');
                        element.click();
                        return true;
                    }}
                    
                    // Provo con selettori CSS generici ma basati sull'ID estratto
                    element = document.querySelector("[id^='cf-chl-widget-{base_id.split('-').pop()}']");
                    if (element) {{
                        console.log('Trovato elemento con selettore parte finale ID: {base_id.split("-").pop()}');
                        element.click();
                        return true;
                    }}
                    
                    // Provo con qualsiasi elemento CloudFlare
                    element = document.querySelector("[id^='cf-chl-widget']");
                    if (element) {{
                        console.log('Trovato elemento con selettore generico');
                        element.click();
                        return true;
                    }}
                    
                    console.log('Nessun elemento CloudFlare trovato');
                    return false;
                """)
                
                if js_result:
                    logger.info(f"CloudFlare CAPTCHA {base_id} cliccato via JavaScript")
                    return
                else:
                    logger.warning("JavaScript non ha trovato elementi CloudFlare cliccabili")
            except Exception as e:
                logger.warning(f"Tentativo JavaScript fallito: {str(e)[:100]}")
        else:
            logger.debug("Nessun elemento CloudFlare rilevato")
            
    except Exception as e:
        logger.error(f"Errore nella gestione CAPTCHA: {str(e)[:100]}")

# ==========================
# Avvio script
# ==========================
if __name__ == "__main__":
    main()