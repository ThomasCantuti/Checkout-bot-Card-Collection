from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# ==========================
# User data compilation
# ==========================
def compiling_form(driver, user_data):
    """
    After adding the product to the cart,
    navigate to the checkout page and fill in the forms.
    """
    proceed_to_checkout_button = WebDriverWait(driver, 11).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div/div[2]/div[1]/div[2]/div[2]/div[1]/div[1]/div[3]/div[3]/a'))
    )
    proceed_to_checkout_button.click()
    
    # Form filling
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="billing.first_name"]').send_keys(user_data["nome"])
    driver.find_element(By.XPATH, '//*[@id="billing.last_name"]').send_keys(user_data["cognome"])
    driver.find_element(By.XPATH, '//*[@id="billing.address_1"]').send_keys(user_data["indirizzo"])
    driver.find_element(By.XPATH, '//*[@id="billing.address_2"]').send_keys(user_data["civico"])
    driver.find_element(By.XPATH, '//*[@id="billing.postcode"]').send_keys(user_data["cap"])
    driver.find_element(By.XPATH, '//*[@id="billing.city"]').send_keys(user_data["citta"])
    dropdown = driver.find_element(By.CSS_SELECTOR, ".choices__inner")
    dropdown.click()
    time.sleep(1)
    option = driver.find_element(By.XPATH, f"//div[@class='choices__item choices__item--choice choices__item--selectable' and @data-value='{user_data['provincia']}']")
    option.click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="billing.phone"]').send_keys(user_data["telefono"])
    driver.find_element(By.XPATH, '//*[@id="billing_email"]').send_keys(user_data["email"])
    
    next_button = driver.find_element(By.XPATH, '//*[@id="step_address_buttons"]/button')
    next_button.click()