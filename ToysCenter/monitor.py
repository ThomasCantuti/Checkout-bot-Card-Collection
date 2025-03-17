from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Utility.utils import cookie_accept, captcha_solver_cloudflare

# ==========================
# Configuration
# ==========================
REFRESH_INTERVAL = 2


# ==========================
# Monitoring and adding to cart
# ==========================
def monitor_and_add_to_cart(driver, website_url, website_key):
    """
    Visita la pagina del prodotto e verifica periodicamente
    la disponibilità senza ricaricare completamente la pagina.
    """
    driver.implicitly_wait(REFRESH_INTERVAL)
    driver.get(website_url)
    print("Pagina caricata")
    time.sleep(1)
    
    product_found = False
    cookie_accept(driver)
    
    # Risolvi il captcha iniziale se presente
    captcha_solver_cloudflare(driver, website_url, website_key)
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
                    captcha_solver_cloudflare(driver, website_url, website_key)
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
                    captcha_solver_cloudflare(driver, website_url, website_key)
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