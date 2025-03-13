from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import string
import random
import time
import json

PRODUCT_URL = "https://www.toyscenter.it/my-account/"

USER_DATA = json.load(open("data.json"))

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

    # Compilazione form
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
    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(USER_DATA["indirizzo"])
    driver.find_element(By.XPATH, '//*[@id="email_confirm"]').send_keys(USER_DATA["indirizzo"])
    driver.find_element(By.XPATH, '//*[@id="customer_phone_"]').send_keys(USER_DATA["telefono"])
    USER_DATA["password"] = genera_password_sicura(USER_DATA)
    json.dump(USER_DATA, open("data.json", "w"), indent=4)
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(USER_DATA["password"])
    driver.find_element(By.XPATH, '//*[@id="password_confirm"]').send_keys(USER_DATA["password"])

    # Accettazione privacy
    toggle_checkbox = driver.find_element(By.NAME, "gdpr_privacy")
    driver.execute_script("arguments[0].click();", toggle_checkbox)
    
    # Click su "Creare account"
    submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    driver.execute_script("arguments[0].click();", submit_button)
    
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