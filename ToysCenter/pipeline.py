import undetected_chromedriver as uc
import time
from dotenv import load_dotenv
import os
import json
from monitor import monitor_and_add_to_cart
from user_data_compiling import compiling_form
from payment import payment_and_confirmation

load_dotenv()
REFRESH_INTERVAL = 2
TOYS_CENTER_URL = os.environ.get('TOYS_CENTER_URL')
TOYS_CENTER_KEY = os.environ.get('TOYS_CENTER_KEY')
ROOT_PATH = os.environ.get('ROOT_PATH')
USER_PATH = os.path.join(ROOT_PATH, "Data", "alle.json")
USER_DATA = json.load(open(USER_PATH))

# ==========================
# Main Function
# ==========================
def main():
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)

    try:
        # 1. MONITORING
        print("Starting monitoring...")
        monitor_and_add_to_cart(driver, TOYS_CENTER_URL, TOYS_CENTER_KEY)
        print("End of monitoring")

        # 2. AUTOMATIC FORM FILLING & CHECKOUT
        print("Starting automatic compilation...")
        compiling_form(driver, USER_DATA)
        print("End of automatic compilation")

        # 3. PAYMENT
        print("Starting payment...")
        payment_and_confirmation(driver, USER_DATA)
        print("End of payment")

        time.sleep(5)
        print("Procedure completed!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        time.sleep(5)
        driver.quit()


if __name__ == "__main__":
    main()