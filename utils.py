from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import capsolver
import json


# ==========================
# Bypass Captcha Cloudflare
# ==========================
def bypass_cloudflare_captcha(driver, product_url):
    settings = json.loads(open("settings.json", "r", encoding="utf-8").read())

    # Initialize capsolver with your API key
    capsolver.api_key = settings["captcha_providers"]["capsolver"]

    # Load the inject.js file content
    with open("inject.js", "r", encoding="utf-8") as f:
        inject_js_content = f.read()

        try:
            # Solve the Turnstile CAPTCHA
            solution = capsolver.solve({
                "type": "AntiTurnstileTaskProxyLess",  # Required. Use 'AntiTurnstileTask' if using proxies or 'AntiTurnstileTaskProxyLess' if not.
                "websiteKey": "0x4AAAAAAA_slGZ9sK4UREXX",  # Required. The public key of the domain, often called the 'site key.'
                "websiteURL": product_url,  # Required. The URL where the CAPTCHA is located.
            })

            token = solution.get('token')
            print("CAPTCHA Solved Token:", token)

            # Start Selenium WebDriver
            # driver = webdriver.Chrome()

            # print(inject_js_content)

            # Inject JavaScript from local file
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": inject_js_content}
            )

            # Navigate to the target page
            driver.get(product_url)

            # Wait for the CAPTCHA response input
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "cf-turnstile-response")))
            
            # Inject the CAPTCHA token
            driver.execute_script("""
                if (window.turnstile && typeof window.tsCallback === "function") {
                    window.tsCallback(arguments[0]);
                }
            """, token)

        except:
            print("Errore durante il bypass del captcha")
            pass


# ==========================
# Gestione cookie
# ==========================
def cookie_accept(driver):
    try:
        cookie_accept_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")  
        cookie_accept_btn.click()
        print("Banner cookie chiuso")
    except:
        print("Nessun banner cookie trovato")