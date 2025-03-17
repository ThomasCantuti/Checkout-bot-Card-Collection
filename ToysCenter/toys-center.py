from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from dotenv import load_dotenv
import time
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Utility.utils import cookie_accept, captcha_solver_cloudflare


# ==========================
# Configurazione
# ==========================
load_dotenv()

TOYS_CENTER_URL = os.environ.get('TOYS_CENTER_URL')
TOYS_CENTER_KEY = os.environ.get('TOYS_CENTER_KEY')
ROOT_PATH = os.environ.get('ROOT_PATH')
REFRESH_INTERVAL = 2
USER_PATH = os.path.join(ROOT_PATH, "Data", "alle.json")
USER_DATA = json.load(open(USER_PATH))


# ==========================
# Funzione principale
# ==========================
def main():
    # Inizializza il webdriver (Chrome in questo caso)
    # Assicurati di aver installato correttamente chromedriver
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    driver.implicitly_wait(REFRESH_INTERVAL)
    driver.get(TOYS_CENTER_URL)
    print("Pagina caricata")

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
    Visita la pagina del prodotto e verifica periodicamente
    la disponibilità senza ricaricare completamente la pagina.
    """
    product_found = False
    cookie_accept(driver)
    
    # Risolvi il captcha iniziale se presente
    captcha_solver_cloudflare(driver, TOYS_CENTER_URL, TOYS_CENTER_KEY)
    time.sleep(5)
    print("Captcha iniziale controllato")
    
    while not product_found:
        # Verifica la disponibilità senza ricaricare la pagina
        # Questo script controlla il contenuto del pulsante tramite JavaScript
        button_text = driver.execute_script("""
            try {
                // Selettore più specifico che esclude il pulsante "Ritira in Negozio"
                const button = document.querySelector('button.single_add_to_cart_button:not([data-product_type="pay_and_collect"])');
                if (button) {
                    // Cerca il paragrafo con data-add-to-cart-button
                    const paragraph = button.querySelector('p[data-add-to-cart-button]');
                    if (paragraph) {
                        return paragraph.textContent.trim().toLowerCase();
                    }
                    // Se non trova il paragrafo specifico, controlla il testo del pulsante
                    return button.textContent.trim().toLowerCase();
                }
                return null;
            } catch (e) {
                console.error("Errore durante la ricerca del pulsante:", e);
                return null;
            }
        """)

        print(f"Testo pulsante: {button_text}")
        time.sleep(REFRESH_INTERVAL)
        
        if button_text == "compra online":
            print("Pulsante 'Compra online' trovato")
            try:
                # Usa lo stesso selettore usato per trovare il testo del pulsante
                add_to_cart_button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.single_add_to_cart_button:not([data-product_type="pay_and_collect"])'))
                )
                add_to_cart_button.click()
                print("Pulsante 'Compra online' cliccato")
                
                # Controlla se appare un captcha dopo il click
                time.sleep(2)  # Breve attesa per l'eventuale apparizione del captcha
                
                # Verifica se è apparso un captcha dopo il click
                turnstile_present = driver.execute_script("""
                    return document.querySelectorAll('iframe[src*="challenges.cloudflare.com"]').length > 0 ||
                           document.querySelector('div[class*="turnstile"]') !== null ||
                           document.querySelector('input[name="cf-turnstile-response"]') !== null;
                """)
                
                if (turnstile_present):
                    # Chiusura di eventuali popup per rilevamento di cloudflare
                    close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[3]/div/div[2]/div[2]/button'))
                    )
                    close_button.click()
                    print("Captcha rilevato dopo aver cliccato 'Compra online'. Risoluzione in corso...")
                    captcha_solver_cloudflare(driver, TOYS_CENTER_URL, TOYS_CENTER_KEY)
                    time.sleep(3)
                    
                    # Dopo aver risolto il captcha, potrebbe essere necessario cliccare nuovamente
                    try:
                        add_to_cart_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.single_add_to_cart_button:not([data-product_type="pay_and_collect"])'))
                        )
                        add_to_cart_button.click()
                        print("Pulsante 'Compra online' cliccato nuovamente dopo risoluzione captcha")
                    except Exception as e:
                        print(f"Impossibile cliccare nuovamente dopo captcha: {str(e)[:100]}")
                
                product_found = True
                
                # Attendi che appaia il pulsante per procedere al carrello
                # Aumento del timeout per dare tempo alla pagina di aggiornare dopo il captcha
                proceed_to_cart = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="page"]/div[4]/footer/div[8]/div/div/div[2]/div/div[2]/div[3]/a'))
                )
                proceed_to_cart.click()
            except Exception as e:
                print(f"Errore nel click o nel procedere al carrello: {str(e)[:100]}")
                
                # Verifica se è apparso un captcha che potrebbe aver causato l'errore
                turnstile_present = driver.execute_script("""
                    return document.querySelectorAll('iframe[src*="challenges.cloudflare.com"]').length > 0 ||
                           document.querySelector('div[class*="turnstile"]') !== null ||
                           document.querySelector('input[name="cf-turnstile-response"]') !== null;
                """)
                
                if turnstile_present:
                    print("Captcha rilevato dopo errore. Risoluzione in corso...")
                    captcha_solver_cloudflare(driver, TOYS_CENTER_URL, TOYS_CENTER_KEY)
                    time.sleep(3)
                else:
                    # Solo in caso di errore ricarichiamo la pagina
                    driver.refresh()
        else:
            # Aggiorna solo parti specifiche della pagina tramite JavaScript
            driver.execute_script("""
                try {
                    // Simulazione di aggiornamento parziale
                    const productContainer = document.querySelector('.product-container');
                    if (productContainer) {
                        productContainer.style.opacity = '0.5';
                        setTimeout(() => { productContainer.style.opacity = '1'; }, 300);
                    }
                } catch (e) {}
            """)


# ==========================
# Procedura di checkout
# ==========================
def proceed_to_checkout(driver):
    """
    Dopo aver aggiunto il prodotto al carrello,
    si naviga alla pagina di checkout e si compilano i form.
    """
    proceed_to_checkout_button = WebDriverWait(driver, 11).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[3]/div[3]/a'))
    )
    proceed_to_checkout_button.click()
    
    # Compilazione form
    time.sleep(1)
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
    Seleziona il metodo di pagamento e inserisce i dati della carta.
    Gestisce gli iframe sicuri di Adyen.
    """
    time.sleep(1)
    
    # Seleziona il metodo di pagamento carta di credito
    cc_radio = WebDriverWait(driver, 1).until(
        EC.element_to_be_clickable((By.ID, "payment_method_adyen"))
    )
    cc_radio.click()
    print("Metodo di pagamento selezionato")
    
    # Attendi che il form di pagamento sia visibile
    WebDriverWait(driver, 1).until(
        EC.visibility_of_element_located((By.ID, "wc_adyen_payment_mount_node"))
    )
    print("Form di pagamento visibile")
    time.sleep(1)  # Attendi il completo caricamento
    
    # Prima gestisci il nome del titolare (campo non in iframe)
    try:
        # Questo è l'unico campo che non è all'interno di un iframe
        holder_name = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='holderName']"))
        )
        holder_name.clear()
        holder_name.send_keys(USER_DATA["titolare_carta"])
        print("Nome del titolare inserito")
    except Exception as e:
        print(f"Errore nell'inserimento del nome del titolare: {e}")
    
    # Ottieni tutti gli iframe
    # time.sleep(2)
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Trovati {len(iframes)} iframe")
    
    # Stampa gli attributi di ogni iframe per debug
    for i, iframe in enumerate(iframes):
        print(f"Iframe {i}: src={iframe.get_attribute('src')}, title={iframe.get_attribute('title')}")
    
    # Approccio con attesa esplicita per ogni iframe e utilizzo di JavaScript
    
    # Numero di carta
    try:
        # Trova l'iframe del numero carta
        card_iframe = None
        for iframe in iframes:
            if "numero di carta" in iframe.get_attribute('title').lower():
                card_iframe = iframe
                break
        
        if card_iframe:
            driver.switch_to.frame(card_iframe)
            print("Passato al frame del numero carta")
            
            # Attendi che la pagina sia completamente caricata
            # time.sleep(2)
            
            # Prova ad inserire il numero di carta usando JavaScript
            driver.execute_script("""
                var inputs = document.querySelectorAll('input');
                for (var i = 0; i < inputs.length; i++) {
                    inputs[i].value = arguments[0];
                    var event = new Event('input', { bubbles: true });
                    inputs[i].dispatchEvent(event);
                }
            """, USER_DATA["numero_carta"])
            
            print("Numero carta inserito via JavaScript")
            driver.switch_to.default_content()
        else:
            print("Iframe per numero carta non trovato")
    except Exception as e:
        print(f"Errore nella gestione del numero carta: {e}")
        driver.switch_to.default_content()
    
    # Data di scadenza
    try:
        # Trova l'iframe della data di scadenza
        exp_iframe = None
        for iframe in iframes:
            if "data di scadenza" in iframe.get_attribute('title').lower():
                exp_iframe = iframe
                break
        
        if exp_iframe:
            driver.switch_to.frame(exp_iframe)
            print("Passato al frame della data di scadenza")
            
            # time.sleep(2)
            
            # Prova ad inserire la data di scadenza usando JavaScript
            driver.execute_script("""
                var inputs = document.querySelectorAll('input');
                for (var i = 0; i < inputs.length; i++) {
                    inputs[i].value = arguments[0];
                    var event = new Event('input', { bubbles: true });
                    inputs[i].dispatchEvent(event);
                }
            """, USER_DATA["scadenza_carta"])
            
            print("Data di scadenza inserita via JavaScript")
            driver.switch_to.default_content()
        else:
            print("Iframe per data di scadenza non trovato")
    except Exception as e:
        print(f"Errore nella gestione della data di scadenza: {e}")
        driver.switch_to.default_content()
    
    # CVV
    try:
        # Trova l'iframe del CVV
        cvv_iframe = None
        for iframe in iframes:
            if "codice di sicurezza" in iframe.get_attribute('title').lower():
                cvv_iframe = iframe
                break
        
        if cvv_iframe:
            driver.switch_to.frame(cvv_iframe)
            print("Passato al frame del CVV")
            
            # time.sleep(2)
            
            # Prova ad inserire il CVV usando JavaScript
            driver.execute_script("""
                var inputs = document.querySelectorAll('input');
                for (var i = 0; i < inputs.length; i++) {
                    inputs[i].value = arguments[0];
                    var event = new Event('input', { bubbles: true });
                    inputs[i].dispatchEvent(event);
                }
            """, USER_DATA["cvv"])
            
            print("CVV inserito via JavaScript")
            driver.switch_to.default_content()
        else:
            print("Iframe per CVV non trovato")
    except Exception as e:
        print(f"Errore nella gestione del CVV: {e}")
        driver.switch_to.default_content()

    input("Premi Invio per continuare con il pagamento o CTRL+C per annullare...")
    
    # Clicca sul bottone di pagamento
    try:
        pay_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, 
                '//*[@id="place_order"]'))
        )
        pay_button.click()
        print("Pulsante di pagamento cliccato")
    except Exception as e:
        print(f"Errore nel click sul pulsante di pagamento: {e}")

    # Attesa per la conferma dell'ordine
    try:
        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"),
                "Grazie per il tuo ordine"
            )
        )
        print("Pagamento completato, ordine confermato.")
    except Exception as e:
        print(f"Attesa conferma ordine non riuscita: {e}")


# ==========================
# Avvio script
# ==========================
if __name__ == "__main__":
    main()