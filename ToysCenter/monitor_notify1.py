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
    Visits the product page and periodically checks
    availability without completely reloading the page.
    """
    driver.implicitly_wait(REFRESH_INTERVAL)
    driver.get(website_url)
    print("Page loaded")
    time.sleep(2)
    
    product_found = False
    cookie_accept(driver)
    
    solve_captcha(driver, website_url, website_key)
        
    time.sleep(5)
    print("Initial captcha checked")
    
    while not product_found:
        # Check availability without reloading the page
        # This script checks the button content via JavaScript
        button_text = driver.execute_script("""
            try {
                // More specific selector that excludes the "Pick up in Store" button
                const button = document.querySelector('button.single_add_to_cart_button:not([data-product_type="pay_and_collect"])');
                if (button) {
                    // Look for paragraph with data-add-to-cart-button
                    const paragraph = button.querySelector('p[data-add-to-cart-button]');
                    if (paragraph) {
                        return paragraph.textContent.trim().toLowerCase();
                    }
                    // If specific paragraph not found, check button text
                    return button.textContent.trim().toLowerCase();
                }
                return null;
            } catch (e) {
                console.error("Error while searching for button:", e);
                return null;
            }
        """)

        print(f"Button text: {button_text}")
        time.sleep(REFRESH_INTERVAL)
        
        if button_text == "compra online":
            print("'Buy online' button found")
            try:
                # Use the same selector used to find the button text
                add_to_cart_button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.single_add_to_cart_button:not([data-product_type="pay_and_collect"])'))
                )
                add_to_cart_button.click()
                print("'Buy online' button clicked")
                product_found = True
                
                # Close any popup for cloudflare detection
                time.sleep(2)
                try:
                    close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[4]/div/div[2]/div[2]/button'))
                    )
                    close_button.click()
                    print("Captcha detected after clicking 'Buy online'. Solving in progress...")
                except:
                    print("No popup detected after captcha resolution")
                
                # Check if a captcha appeared after clicking
                solve_captcha(driver, website_url, website_key)
                
                # Proceed to cart
                if count_product_cart(driver) > 0:
                    print("Product added to cart")
                    try:
                        proceed_to_cart_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[@id="page"]/div[4]/footer/div[8]/div/div/div[2]/div/div[2]/div[3]/a'))
                        )
                        proceed_to_cart_button.click()
                        print("Proceed to cart clicked")
                    except:
                        print("Proceed to cart button from popup not found")
                        try:
                            cart_button = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href*="/cart/"][class*="tw-relative"]'))
                            )
                            cart_button.click()
                            print("Carrello cliccato")
                        except:
                            print("Cart button not found")
                else:
                    print("Product not added to cart")
            except Exception as e:
                print(f"Error in clicking or proceeding to cart")
                solve_captcha(driver, website_url, website_key)
        else:
            # Update only specific parts of the page via JavaScript
            driver.execute_script("""
                try {
                    // Simulation of partial update
                    const productContainer = document.querySelector('.product-container');
                    if (productContainer) {
                        productContainer.style.opacity = '0.5';
                        setTimeout(() => { productContainer.style.opacity = '1'; }, 300);
                    }
                } catch (e) {}
            """)


def solve_captcha(driver, website_url, website_key):
    # Solve initial captcha if present
    turnstile_present = driver.execute_script("""
        return document.querySelector('[data-sitekey="0x4AAAAAAA_slGZ9sK4UREXX"]') !== null
    """)
    
    if not turnstile_present:
        print("Nessun captcha Turnstile trovato nella pagina. Potrebbe essere già risolto o non presente.")
    else:
        print("Captcha Turnstile trovato nella pagina. Procedi con la risoluzione...")
        captcha_solver_cloudflare(driver, website_url, website_key)

def count_product_cart(driver):
    # Ottiene il numero di oggetti nel carrello
    return driver.execute_script("""
        try {
            // Trova l'elemento che mostra il conteggio
            const countElement = document.querySelector('.tw-bg-primary-dark.tw-text-white span[x-html]');
            if (countElement) {
                // Estrae e restituisce il numero come intero
                return parseInt(countElement.textContent.trim());
            }
            
            // Approccio alternativo se il selettore precedente non funziona
            const cartBadge = document.querySelector('span[x-html="get(\'items_count\', 0)"]');
            if (cartBadge) {
                return parseInt(cartBadge.textContent.trim());
            }
            
            return 0; // Se non è possibile trovare l'elemento, assume 0
        } catch (e) {
            console.error("Errore nell'ottenere il conteggio del carrello:", e);
            return 0;
        }
    """)
        