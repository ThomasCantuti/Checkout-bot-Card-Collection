from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# ==========================
# Payment and confirmation
# ==========================
def payment_and_confirmation(driver, user_data):
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
        holder_name.send_keys(user_data["titolare_carta"])
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
            """, user_data["numero_carta"])
            
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
            """, user_data["scadenza_carta"])
            
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
            """, user_data["cvv"])
            
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