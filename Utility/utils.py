from selenium.webdriver.common.by import By
from curl_cffi import requests
import time
import json
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS = json.loads(open(os.path.join(project_root, "settings.json"), "r", encoding="utf-8").read())
CAPSOLVER_API_KEY = SETTINGS["captcha_providers"]["capsolver"]


# ==========================
# Bypass Captcha Cloudflare
# ==========================
def solvecf(website_url, website_key, metadata_action=None, metadata_cdata=None):
    url = "https://api.capsolver.com/createTask"
    task = {
        "type": "AntiTurnstileTaskProxyLess",
        "websiteURL": website_url,
        "websiteKey": website_key,
    }
    if metadata_action or metadata_cdata:
        task["metadata"] = {}
        if metadata_action:
            task["metadata"]["action"] = metadata_action
        if metadata_cdata:
            task["metadata"]["cdata"] = metadata_cdata
    data = {
        "clientKey": CAPSOLVER_API_KEY,
        "task": task
    }
    response_data = requests.post(url, json=data).json()
    # print(response_data)
    return response_data['taskId']


def solutionGet(taskId):
    url = "https://api.capsolver.com/getTaskResult"
    status = ""
    while status != "ready":
        data = {"clientKey": CAPSOLVER_API_KEY, "taskId": taskId}
        response_data = requests.post(url, json=data).json()
        # print(response_data)
        status = response_data.get('status', '')
        print(status)
        if status == "ready":
            return response_data['solution']

        time.sleep(2)


def captcha_solver_cloudflare(driver, website_url, website_key):
    click_cloudflare_button(driver)
    
    # Ottieni la soluzione dal servizio Capsolver
    taskId = solvecf(website_url=website_url, website_key=website_key)
    solution = solutionGet(taskId)
    # print(f"Solution: {solution}")
    
    if solution:
        token = solution['token']
        print("Solved Turnstile Captcha")
        
        # Inietta il token direttamente
        script = f"""
        try {{
            // Cerca l'input nascosto del captcha
            let turnstileInput = document.querySelector('input[name="cf-turnstile-response"]');
            if (turnstileInput) {{
                turnstileInput.value = "{token}";
                console.log("Token inserito nell'input nascosto");
                return true;
            }}
            return false;
        }} catch (e) {{
            console.error("Errore: ", e);
            return false;
        }}
        """
        
        success = driver.execute_script(script)
        print(f"Injection token success: {success}")
        
        # Verifica se il captcha è ancora visibile
        captcha_still_visible = driver.execute_script("""
            const turnstileIframes = document.querySelectorAll('iframe[src*="challenges.cloudflare.com"]');
            return turnstileIframes.length > 0;
        """)
        
        if captcha_still_visible:
            print("ATTENZIONE: Il captcha sembra ancora visibile dopo il tentativo di risoluzione.")
        else:
            print("Il captcha non è più visibile, potrebbe essere stato risolto.")
    
    click_cloudflare_button(driver)


def click_cloudflare_button(driver):
    # Try to click the captcha button directly
    try:
        print("Tentativo di cliccare direttamente sul pulsante del captcha...")
        
        # Trova il container del Turnstile o il pulsante
        captcha_elements = driver.find_elements(By.CSS_SELECTOR, 
            "iframe[src*='challenges.cloudflare.com'], div[class*='turnstile'], button[class*='captcha']")
        if captcha_elements:
            for element in captcha_elements:
                try:
                    element.click()
                    print(f"Cliccato su elemento captcha: {element.get_attribute('class') or element.tag_name}")
                except Exception as e:
                    print(f"Non è stato possibile cliccare sull'elemento captcha")
        else:
            print("Nessun elemento captcha cliccabile trovato")
    except Exception as e:
        print(f"Errore durante il tentativo di cliccare sul captcha")


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