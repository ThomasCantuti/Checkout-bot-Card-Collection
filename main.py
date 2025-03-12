from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

# ==========================
# Configurazione
# ==========================

PRODUCT_URL = "https://www.esempio.com/pokemon-card-prodotto"  # URL prodotto
CHECKOUT_URL = "https://www.esempio.com/checkout"            # URL checkout (varia a seconda del sito)
REFRESH_INTERVAL = 5  # secondi tra un controllo e l'altro

# Dati utente (ES: potrebbero essere caricati da un file sicuro/criptato)
USER_DATA = {
    "nome": "Mario",
    "cognome": "Rossi",
    "indirizzo": "Via Esempio 123",
    "citta": "Roma",
    "cap": "00100",
    "telefono": "1234567890",
    "email": "mario.rossi@example.com",
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
    driver = webdriver.Chrome()

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
    
    while not product_found:
        driver.get(PRODUCT_URL)

        try:
            # Attende la presenza del bottone per un tot di secondi
            add_to_cart_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aggiungi al carrello')]"))
            )
            # Se trova il bottone, clicca
            add_to_cart_button.click()
            product_found = True
            print("Prodotto disponibile e aggiunto al carrello!")
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
    driver.get(CHECKOUT_URL)

    # Attendere che i campi siano presenti
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "firstname"))
    )

    # Compilazione form (ESEMPI: gli elementi e i name vanno adattati al sito reale)
    driver.find_element(By.NAME, "firstname").send_keys(USER_DATA["nome"])
    driver.find_element(By.NAME, "lastname").send_keys(USER_DATA["cognome"])
    driver.find_element(By.NAME, "address").send_keys(USER_DATA["indirizzo"])
    driver.find_element(By.NAME, "city").send_keys(USER_DATA["citta"])
    driver.find_element(By.NAME, "postal").send_keys(USER_DATA["cap"])
    driver.find_element(By.NAME, "phone").send_keys(USER_DATA["telefono"])
    driver.find_element(By.NAME, "email").send_keys(USER_DATA["email"])

    # Poi si clicca sul bottone di avanzamento
    # (sul sito reale potrebbe essere 'Continua', 'Next', ecc.)
    next_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continua')]")
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