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
    try:
        with open("inject.js", "r", encoding="utf-8") as f:
            inject_js_content = f.read()
    except FileNotFoundError:
        print("Errore: File inject.js non trovato")
        return False
    except Exception as e:
        print(f"Errore nella lettura del file inject.js: {str(e)}")
        return False

    try:
        # Solve the Turnstile CAPTCHA
        solution = capsolver.solve({
            "type": "AntiTurnstileTaskProxyLess",  # Required. Use 'AntiTurnstileTask' if using proxies or 'AntiTurnstileTaskProxyLess' if not.
            "websiteKey": "0x4AAAAAAA_slGZ9sK4UREXX",  # Required. The public key of the domain, often called the 'site key.'
            "websiteURL": product_url,  # Required. The URL where the CAPTCHA is located.
        })

        token = solution.get('token')
        if not token:
            print("Errore: Token CAPTCHA non ottenuto")
            return False
            
        print("CAPTCHA Solved Token:", token)

        # Inject JavaScript from local file
        try:
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": inject_js_content}
            )
        except Exception as e:
            print(f"Errore nell'iniezione dello script: {str(e)}")
            return False

        # Navigate to the target page
        try:
            driver.get(product_url)
        except Exception as e:
            print(f"Errore nel caricamento della pagina {product_url}: {str(e)}")
            return False

        # Wait for the CAPTCHA response input
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "cf-turnstile-response")))
        except Exception as e:
            print(f"Timeout o errore nell'attesa dell'elemento cf-turnstile-response: {str(e)}")
            return True
        
        # Inject the CAPTCHA token
        try:
            driver.execute_script("""
                if (window.turnstile && typeof window.tsCallback === "function") {
                    window.tsCallback(arguments[0]);
                }
            """, token)
            return True
        except Exception as e:
            print(f"Errore nell'iniezione del token CAPTCHA: {str(e)}")
            return False

    except capsolver.error.CapsolverError as e:
        print(f"Errore Capsolver durante la risoluzione del CAPTCHA: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        print(f"Errore nella decodifica JSON della risposta: {str(e)}")
        return False
    except Exception as e:
        print(f"Errore durante il bypass del captcha: {str(e)}")
        return False


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