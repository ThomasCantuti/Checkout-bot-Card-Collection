from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import undetected_chromedriver as uc
import time

# ==========================
# Configurazione
# ==========================

PRODUCT_URL = "https://www.toyscenter.it/prodotto/funko-pop-pokemon-mew-643/"  # URL prodotto
REFRESH_INTERVAL = 10  # secondi tra un controllo e l'altro

USER_DATA = {
    "nome": "Mario",
    "cognome": "Rossi",
    "indirizzo": "Via Esempio",
    "civico": "123",
    "citta": "Roma",
    "provincia": "RM",
    "cap": "00100",
    "telefono": "1234567890",
    "email": "random@41032domainname.it",
    "metodo_pagamento": "carta_di_credito",
    "numero_carta": "4111 1111 1111 1111",
    "scadenza_carta": "12/25",
    "cvv": "123"
}

# ==========================
# Funzione principale
# ==========================

def main():
    # Inizializza il webdriver (Chrome in questo caso)
    # Assicurati di aver installato correttamente chromedriver
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    driver.implicitly_wait(10)

    try:
        # 1. MONITORAGGIO
        monitor_and_add_to_cart(driver)

        # 2. COMPILAZIONE AUTOMATICA & CHECKOUT
        proceed_to_checkout(driver)

        # 3. PAGAMENTO
        payment_and_confirmation(driver)

        print("Procedura completata!")

    except Exception as e:
        print(f"Si è verificato un errore: {e}")
    finally:
        # Chiude il browser alla fine
        time.sleep(5)  # per debug, poi puoi togliere o abbassare il tempo
        driver.quit()

# ==========================
# Monitoraggio e aggiunta al carrello
# ==========================
def monitor_and_add_to_cart(driver):
    """
    Visita la pagina del prodotto e aggiorna periodicamente
    fino a trovare il bottone di 'Aggiungi al carrello'.
    Non appena lo trova, clicca e interrompe il loop.
    """
    product_found = False
    driver.get(PRODUCT_URL)
    
    while not product_found:

        try:
            # Attende la presenza del bottone per un tot di secondi
            add_to_cart_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div[2]/div[2]/div[2]/div[1]/div[2]/form/div[2]/div/div[3]/button'))
            )
            # Se trova il bottone, clicca
            add_to_cart_button.click()
            product_found = True
            
            proceed_to_cart = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="page"]/div[4]/footer/div[8]/div/div/div[2]/div/div[2]/div[3]/a'))
            )
            # Se trova il bottone, clicca
            proceed_to_cart.click()
        except:
            print("Prodotto non disponibile, ritento fra pochi secondi...")
            time.sleep(REFRESH_INTERVAL)

# ==========================
# Procedura di checkout
# ==========================
def proceed_to_checkout(driver):
    """
    Dopo aver aggiunto il prodotto al carrello,
    si naviga alla pagina di checkout e si compilano i form.
    """
    # A volte, dopo l'aggiunta al carrello, il sito ridirige direttamente
    # Oppure potresti dover cliccare manualmente su un link 'Vai al carrello'
    # Qui facciamo finta che basti andare su CHECKOUT_URL

    proceed_to_checkout_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[3]/div[3]/a'))
    )
    proceed_to_checkout_button.click()
    
    # try to login
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div[2]/div[2]/div/div[1]/div/div/div[2]/div[2]/button'))
    )
    login_button.click()
    
    user_login_field = driver.find_element(By.XPATH, '//*[@id="user_login"]')
    user_login_field.send_keys(USER_DATA["email"])
    
    continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[2]/div/div/div[1]/div[3]/button'))
    )
    continue_button.click()
    
    time.sleep(3)
    
    # /html/body/div[2]/div[2]/div/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[2]
    if driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[2]/div/div/div[1]/div[1]/p[2]').is_displayed():
        print("Utente non esistente")
        # close and register
        close_button = driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div/div/div[2]/div/div/div[1]/div[4]')
        close_button.click()
    else:
        print("Utente esistente")
        user_password_field = driver.find_element(By.XPATH, '//*[@id="user_login"]')
        user_password_field.send_keys(USER_DATA["password"])
        # continua con la redirezione alla pagina di checkout

    # Compilazione form
    driver.find_element(By.XPATH, '//*[@id="billing.first_name"]').send_keys(USER_DATA["nome"])
    driver.find_element(By.XPATH, '//*[@id="billing.last_name"]').send_keys(USER_DATA["cognome"])
    driver.find_element(By.XPATH, '//*[@id="billing.address_1"]').send_keys(USER_DATA["indirizzo"])
    driver.find_element(By.XPATH, '//*[@id="billing.address_2"]').send_keys(USER_DATA["civico"])
    driver.find_element(By.XPATH, '//*[@id="billing.postcode"]').send_keys(USER_DATA["cap"])
    driver.find_element(By.XPATH, '//*[@id="billing.city"]').send_keys(USER_DATA["citta"])
    dropdown = driver.find_element(By.CSS_SELECTOR, ".choices__inner")
    dropdown.click()
    time.sleep(1)
    option = driver.find_element(By.XPATH, f"//div[@class='choices__item choices__item--choice choices__item--selectable' and @data-value='{USER_DATA['provincia']}']")
    option.click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="billing.phone"]').send_keys(USER_DATA["telefono"])
    driver.find_element(By.XPATH, '//*[@id="billing_email"]').send_keys(USER_DATA["email"])
    
    next_button = driver.find_element(By.XPATH, '//*[@id="step_address_buttons"]/button')
    next_button.click()

# ==========================
# Pagamento e conferma
# ==========================
def payment_and_confirmation(driver):
    """
    Seleziona il metodo di pagamento e inserisce i dati della carta
    (o PayPal, a seconda del sito). Quindi conferma.
    """
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "cardnumber"))
    )

    # Inserisci i dati della carta (esempio generico)
    driver.find_element(By.NAME, "cardnumber").send_keys(USER_DATA["numero_carta"])
    driver.find_element(By.NAME, "cardexpiration").send_keys(USER_DATA["scadenza_carta"])
    driver.find_element(By.NAME, "cardcvv").send_keys(USER_DATA["cvv"])

    # Clicca sul bottone di pagamento
    pay_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Paga ora')]")
    pay_button.click()

    # Attendere una pagina di conferma (o un messaggio)
    # (Esempio: cerca un elemento che dica "Grazie per il tuo ordine")
    WebDriverWait(driver, 20).until(
        EC.text_to_be_present_in_element(
            (By.TAG_NAME, "body"),  # o un locatore più mirato
            "Grazie per il tuo ordine"
        )
    )
    print("Pagamento completato, ordine confermato.")

# ==========================
# Avvio script
# ==========================
if __name__ == "__main__":
    main()