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
    
    # Solve initial captcha if present
    turnstile_present = driver.execute_script("""
        return document.querySelectorAll('iframe[src*="challenges.cloudflare.com"]').length > 0 ||
               document.querySelector('div[class*="turnstile"]') !== null ||
               document.querySelector('input[name="cf-turnstile-response"]') !== null;
    """)
    
    if not turnstile_present:
        print("Nessun captcha Turnstile trovato nella pagina. Potrebbe essere già risolto o non presente.")
    else:
        print("Captcha Turnstile trovato nella pagina. Procedi con la risoluzione...")
        captcha_solver_cloudflare(driver, website_url, website_key)
        
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
                
                # Check if a captcha appears after clicking
                time.sleep(2)  # Short wait for possible captcha appearance
                
                # Check if a captcha appeared after clicking
                turnstile_present = driver.execute_script("""
                    return document.querySelectorAll('iframe[src*="challenges.cloudflare.com"]').length > 0 ||
                           document.querySelector('div[class*="turnstile"]') !== null ||
                           document.querySelector('input[name="cf-turnstile-response"]') !== null;
                """)
                
                if (turnstile_present):
                    # Close any popup for cloudflare detection
                    close_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[4]/div/div[2]/div[2]/button'))
                    )
                    close_button.click()
                    print("Captcha detected after clicking 'Buy online'. Solving in progress...")
                    captcha_solver_cloudflare(driver, website_url, website_key)
                    time.sleep(3)
                    
                    # Click the button again after captcha resolution
                    add_to_cart_button = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.single_add_to_cart_button:not([data-product_type="pay_and_collect"])'))
                    )
                    add_to_cart_button.click()
                    print("'Buy online' button clicked")
                    
                    # After solving the captcha, it might be necessary to click again
                    try:
                        add_to_cart_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.single_add_to_cart_button:not([data-product_type="pay_and_collect"])'))
                        )
                        add_to_cart_button.click()
                        print("'Buy online' button clicked again after captcha resolution")
                    except Exception as e:
                        print(f"Unable to click again after captcha: {str(e)[:100]}")
                
                product_found = True
                
                # Wait for the button to proceed to cart to appear
                # Increased timeout to give the page time to update after captcha
                proceed_to_cart = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="page"]/div[4]/footer/div[8]/div/div/div[2]/div/div[2]/div[3]/a'))
                )
                proceed_to_cart.click()
            except Exception as e:
                print(f"Error in clicking or proceeding to cart: {str(e)[:100]}")
                
                # Check if a captcha appeared that might have caused the error
                turnstile_present = driver.execute_script("""
                    return document.querySelectorAll('iframe[src*="challenges.cloudflare.com"]').length > 0 ||
                           document.querySelector('div[class*="turnstile"]') !== null ||
                           document.querySelector('input[name="cf-turnstile-response"]') !== null;
                """)
                
                if turnstile_present:
                    print("Captcha detected after error. Solving in progress...")
                    captcha_solver_cloudflare(driver, website_url, website_key)
                    time.sleep(3)
                '''else:
                    # Only reload the page in case of error
                    driver.refresh()'''
            
            # Attende e clicca sul pulsante del carrello
            try:
                cart_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[href*="/cart/"][class*="tw-relative"]'))
                )
                cart_button.click()
                print("Clicked on cart button")
                break
            except Exception as e:
                print(f"Error in clicking on cart button: {str(e)[:100]}")
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
        