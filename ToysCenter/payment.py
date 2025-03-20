from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# ==========================
# Payment and confirmation
# ==========================
def payment_and_confirmation(driver, user_data):
    """
    Selects the payment method and enters card details.
    Handles Adyen secure iframes.
    """
    time.sleep(1)
    
    # Select credit card payment method
    cc_radio = WebDriverWait(driver, 1).until(
        EC.element_to_be_clickable((By.ID, "payment_method_adyen"))
    )
    cc_radio.click()
    print("Payment method selected")
    
    # Wait for payment form to be visible
    WebDriverWait(driver, 1).until(
        EC.visibility_of_element_located((By.ID, "wc_adyen_payment_mount_node"))
    )
    print("Payment form visible")
    time.sleep(1)  # Wait for complete loading
    
    # First handle the cardholder name (field not in iframe)
    try:
        # This is the only field that is not inside an iframe
        holder_name = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='holderName']"))
        )
        holder_name.clear()
        holder_name.send_keys(user_data["titolare_carta"])
        print("Cardholder name entered")
    except Exception as e:
        print(f"Error entering cardholder name: {e}")
    
    # Get all iframes
    # time.sleep(2)
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Found {len(iframes)} iframes")
    
    # Print attributes of each iframe for debugging
    for i, iframe in enumerate(iframes):
        print(f"Iframe {i}: src={iframe.get_attribute('src')}, title={iframe.get_attribute('title')}")
    
    # Approach with explicit wait for each iframe and using JavaScript
    
    # Card number
    try:
        # Find the card number iframe
        card_iframe = None
        for iframe in iframes:
            if "numero di carta" in iframe.get_attribute('title').lower():
                card_iframe = iframe
                break
        
        if card_iframe:
            driver.switch_to.frame(card_iframe)
            print("Switched to card number frame")
            
            # Wait for the page to fully load
            # time.sleep(2)
            
            # Try to enter card number using JavaScript
            driver.execute_script("""
                var inputs = document.querySelectorAll('input');
                for (var i = 0; i < inputs.length; i++) {
                    inputs[i].value = arguments[0];
                    var event = new Event('input', { bubbles: true });
                    inputs[i].dispatchEvent(event);
                }
            """, user_data["numero_carta"])
            
            print("Card number entered via JavaScript")
            driver.switch_to.default_content()
        else:
            print("Card number iframe not found")
    except Exception as e:
        print(f"Error handling card number: {e}")
        driver.switch_to.default_content()
    
    # Expiration date
    try:
        # Find the expiration date iframe
        exp_iframe = None
        for iframe in iframes:
            if "data di scadenza" in iframe.get_attribute('title').lower():
                exp_iframe = iframe
                break
        
        if exp_iframe:
            driver.switch_to.frame(exp_iframe)
            print("Switched to expiration date frame")
            
            # time.sleep(2)
            
            # Try to enter expiration date using JavaScript
            driver.execute_script("""
                var inputs = document.querySelectorAll('input');
                for (var i = 0; i < inputs.length; i++) {
                    inputs[i].value = arguments[0];
                    var event = new Event('input', { bubbles: true });
                    inputs[i].dispatchEvent(event);
                }
            """, user_data["scadenza_carta"])
            
            print("Expiration date entered via JavaScript")
            driver.switch_to.default_content()
        else:
            print("Expiration date iframe not found")
    except Exception as e:
        print(f"Error handling expiration date: {e}")
        driver.switch_to.default_content()
    
    # CVV
    try:
        # Find the CVV iframe
        cvv_iframe = None
        for iframe in iframes:
            if "codice di sicurezza" in iframe.get_attribute('title').lower():
                cvv_iframe = iframe
                break
        
        if cvv_iframe:
            driver.switch_to.frame(cvv_iframe)
            print("Switched to CVV frame")
            
            # time.sleep(2)
            
            # Try to enter CVV using JavaScript
            driver.execute_script("""
                var inputs = document.querySelectorAll('input');
                for (var i = 0; i < inputs.length; i++) {
                    inputs[i].value = arguments[0];
                    var event = new Event('input', { bubbles: true });
                    inputs[i].dispatchEvent(event);
                }
            """, user_data["cvv"])
            
            print("CVV entered via JavaScript")
            driver.switch_to.default_content()
        else:
            print("CVV iframe not found")
    except Exception as e:
        print(f"Error handling CVV: {e}")
        driver.switch_to.default_content()

    input("Press Enter to continue with payment or CTRL+C to cancel...")
    
    # Click the payment button
    try:
        pay_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, 
                '//*[@id="place_order"]'))
        )
        pay_button.click()
        print("Payment button clicked")
    except Exception as e:
        print(f"Error clicking payment button: {e}")

    # Wait for order confirmation
    try:
        WebDriverWait(driver, 20).until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"),
                "Grazie per il tuo ordine"
            )
        )
        print("Payment completed, order confirmed.")
    except Exception as e:
        print(f"Waiting for order confirmation failed: {e}")