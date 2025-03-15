import os
import json
import time
import requests
import random
import capsolver
from selenium.webdriver.common.by import By


# ==========================
# Bypass Captcha Cloudflare
# ==========================
def bypass_cloudflare_captcha(driver, settings_path="settings.json", proxies_path="proxies.txt"):
    """
    Utilizza Capsolver per bypassare il captcha Cloudflare Turnstile.
    
    Args:
        driver: WebDriver Selenium
        settings_path: Percorso del file settings.json
        proxies_path: Percorso del file con la lista di proxy
        
    Returns:
        bool: True se il bypass è riuscito, False altrimenti
    """
    print("⚡ Tentativo di bypass del captcha Cloudflare...")
    
    # Carica le impostazioni
    try:
        if not os.path.exists(settings_path):
            print(f"❌ File {settings_path} non trovato!")
            return False
            
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        # Estrai la chiave API
        if 'captcha_providers' not in settings or 'capsolver' not in settings['captcha_providers']:
            print("❌ API key Capsolver non trovata!")
            return False
            
        api_key = settings['captcha_providers']['capsolver']
        if not api_key:
            print("❌ API key Capsolver non configurata!")
            return False
            
        # Configura la libreria capsolver
        capsolver.api_key = api_key
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False
    
    try:
        # Ottieni l'URL corrente e rileva il sitekey
        current_url = driver.current_url
        print(f"🌐 URL corrente: {current_url}")
        
        # Cerca di estrarre il sitekey di Turnstile dalla pagina
        try:
            site_key = driver.execute_script("""
                // Cerca il sitekey nei widget di Turnstile
                var elements = document.querySelectorAll('[data-sitekey]');
                for (var i = 0; i < elements.length; i++) {
                    var key = elements[i].getAttribute('data-sitekey');
                    if (key && key.startsWith('0x')) {
                        return key;
                    }
                }
                
                // Cerca anche in elementi con classe turnstile o cf-turnstile
                var turnstileElements = document.querySelectorAll('.turnstile, .cf-turnstile, [class*="turnstile"]');
                for (var i = 0; i < turnstileElements.length; i++) {
                    var key = turnstileElements[i].getAttribute('data-sitekey');
                    if (key) return key;
                }
                
                // Se non lo trova, cerca nei parametri della funzione di render
                if (typeof window.turnstile !== 'undefined' && window.turnstile.render) {
                    // Guarda nei parametri di turnstile.render
                    var originalRender = window.turnstile.render;
                    var found = null;
                    window.turnstile.render = function(container, params) {
                        if (params && params.sitekey) {
                            found = params.sitekey;
                        }
                        return originalRender(container, params);
                    };
                    // Tenta di triggerare alcuni render
                    try { window.turnstile.render(); } catch (e) {}
                    // Ripristina la funzione originale
                    window.turnstile.render = originalRender;
                    if (found) return found;
                }
                
                // Fallback a un sitekey generico per Cloudflare
                return "0x4AAAAAAAB9pNxxdYOSfJy7";
            """)
            print(f"🔑 Rilevato sitekey: {site_key}")
        except Exception as e:
            print(f"⚠️ Impossibile rilevare il sitekey: {e}")
            # Usa un sitekey generico per Cloudflare
            site_key = "0x4AAAAAAAB9pNxxdYOSfJy7"
            print(f"🔑 Utilizzo sitekey generico: {site_key}")
        
        print("📤 Risoluzione captcha in corso...")
        
        # Usa la libreria capsolver direttamente
        try:
            solution = capsolver.solve({
                "type": "AntiTurnstileTaskProxyLess",
                "websiteURL": current_url,
                "websiteKey": site_key
            })
            
            print(f"📋 Risposta API: {json.dumps(solution, indent=2) if solution else 'Nessuna risposta'}")
            
            if solution and "token" in solution:
                token = solution["token"]
                print("✅ Token ricevuto!")
                
                # Trova l'elemento del captcha per ottenere metadati
                action = driver.execute_script("""
                    var action = '';
                    var elements = document.querySelectorAll('[data-action]');
                    for (var i = 0; i < elements.length; i++) {
                        action = elements[i].getAttribute('data-action');
                        if (action) return action;
                    }
                    return '';
                """)
                
                # Nota: Ora applichiamo il token in modi diversi
                success = driver.execute_script(f"""
                    try {{
                        console.log("Tentativo di applicazione token Cloudflare...");
                        
                        // 1. Metodo per siti che usano Turnstile direttamente
                        if (typeof window.turnstile !== 'undefined') {{
                            console.log("Turnstile trovato nella pagina");
                            if (typeof window.turnstile.reset === 'function') {{
                                try {{
                                    window.turnstile.reset();
                                    console.log("Reset turnstile eseguito");
                                }} catch(e) {{
                                    console.error("Errore reset turnstile:", e);
                                }}
                            }}
                            
                            if (typeof window.turnstile.execute === 'function') {{
                                try {{
                                    // Salva la funzione originale
                                    var originalExecute = window.turnstile.execute;
                                    // Sovrascrivi per restituire il token
                                    window.turnstile.execute = function() {{
                                        console.log("Intercettata chiamata a turnstile.execute");
                                        return "{token}";
                                    }};
                                    console.log("Funzione execute sovrascritta");
                                }} catch(e) {{
                                    console.error("Errore override execute:", e);
                                }}
                            }}
                            
                            if (typeof window.turnstile.getResponse === 'function') {{
                                try {{
                                    var originalGetResponse = window.turnstile.getResponse;
                                    window.turnstile.getResponse = function() {{
                                        console.log("Intercettata chiamata a getResponse");
                                        return "{token}";
                                    }};
                                    console.log("Funzione getResponse sovrascritta");
                                }} catch(e) {{
                                    console.error("Errore override getResponse:", e);
                                }}
                            }}
                        }}
                        
                        // 2. Metodo per invio token tramite campi nascosti
                        var inputFieldsModified = false;
                        var tokenInputs = document.querySelectorAll('input[name="cf-turnstile-response"], input[name="g-recaptcha-response"], input[name="h-captcha-response"], input[name="captcha-response"]');
                        if (tokenInputs.length > 0) {{
                            for (var i = 0; i < tokenInputs.length; i++) {{
                                console.log("Impostazione token in campo input:", tokenInputs[i].name);
                                tokenInputs[i].value = "{token}";
                                
                                // Tenta di triggerare eventi per notificare il cambiamento
                                try {{
                                    var event = new Event('input', {{ bubbles: true }});
                                    tokenInputs[i].dispatchEvent(event);
                                    var changeEvent = new Event('change', {{ bubbles: true }});
                                    tokenInputs[i].dispatchEvent(changeEvent);
                                }} catch(e) {{
                                    console.error("Errore eventi:", e);
                                }}
                                inputFieldsModified = true;
                            }}
                            console.log("Token inserito in " + tokenInputs.length + " campi input");
                        }}
                        
                        // Se non trova input specifici, crea un nuovo campo
                        if (!inputFieldsModified) {{
                            try {{
                                console.log("Creazione nuovo campo input per il token");
                                var form = document.querySelector('form');
                                if (form) {{
                                    var input = document.createElement('input');
                                    input.type = 'hidden';
                                    input.name = 'cf-turnstile-response';
                                    input.value = "{token}";
                                    form.appendChild(input);
                                    console.log("Creato nuovo campo input in form");
                                    inputFieldsModified = true;
                                }}
                            }} catch(e) {{
                                console.error("Errore creazione campo:", e);
                            }}
                        }}
                        
                        // 3. Imposta il token come cookie cf_clearance
                        try {{
                            document.cookie = "cf_clearance={token}; path=/; domain=.toyscenter.it; max-age=86400; secure";
                            console.log("Token impostato come cookie");
                        }} catch(e) {{
                            console.error("Errore impostazione cookie:", e);
                        }}
                        
                        // 4. Set globale
                        try {{
                            window.cf_token = "{token}";
                            window.cf_turnstile_response = "{token}";
                            console.log("Token impostato come variabili globali");
                        }} catch(e) {{
                            console.error("Errore variabili globali:", e);
                        }}
                        
                        // 5. Prova a cercare istanze di callback Turnstile e chiamarle
                        try {{
                            var callbackFound = false;
                            if (typeof window._turnstileCb === 'function') {{
                                window._turnstileCb("{token}");
                                callbackFound = true;
                                console.log("Chiamata callback _turnstileCb");
                            }}
                            
                            // Cerca altre possibili callback
                            for (var key in window) {{
                                if (typeof window[key] === 'function' && 
                                    (key.toLowerCase().includes('turnstile') || 
                                     key.toLowerCase().includes('captcha') || 
                                     key.toLowerCase().includes('callback'))) {{
                                    try {{
                                        window[key]("{token}");
                                        console.log("Chiamata potenziale callback:", key);
                                        callbackFound = true;
                                    }} catch(e) {{}}
                                }}
                            }}
                        }} catch(e) {{
                            console.error("Errore callback:", e);
                        }}
                        
                        console.log("Applicazione token completata");
                        return true;
                    }} catch(e) {{
                        console.error("Errore generale nell'applicazione del token:", e);
                        return false;
                    }}
                """)
                
                if success:
                    print("🚀 Token applicato!")
                    
                    # Verifica se ci sono form da inviare
                    form_submitted = driver.execute_script("""
                        try {
                            // Cerca e invia il form che contiene il turnstile
                            var forms = document.querySelectorAll('form');
                            for (var i = 0; i < forms.length; i++) {
                                if (forms[i].querySelector('[data-sitekey], [name="cf-turnstile-response"]')) {
                                    console.log("Invio form con captcha...");
                                    forms[i].submit();
                                    return true;
                                }
                            }
                            return false;
                        } catch(e) {
                            console.error("Errore invio form:", e);
                            return false;
                        }
                    """)
                    
                    if form_submitted:
                        print("📝 Form inviato automaticamente")
                        time.sleep(5)
                    '''else:
                        print("🔄 Ricaricamento pagina...")
                        driver.refresh()
                        time.sleep(5)'''
                    
                    # Aspetta che eventuali reindirizzamenti si completino
                    end_time = time.time() + 10
                    while time.time() < end_time:
                        if "challenge" not in driver.current_url and "cloudflare" not in driver.page_source.lower():
                            break
                        time.sleep(1)
                    
                    # Verifica se il bypass è riuscito
                    if "challenge" not in driver.current_url and "cloudflare" not in driver.page_source.lower():
                        print("🎉 Bypass completato con successo!")
                        return True
                    else:
                        print("⚠️ Token applicato ma captcha ancora presente")
                        
                        # Tentativo alternativo: forzare la navigazione diretta alla pagina di destinazione
                        try:
                            original_url = driver.current_url.split("?__cf_chl")[0].split("?__cf")[0]
                            if "challenge" in driver.current_url and original_url != driver.current_url:
                                print("🔀 Tentativo di navigazione diretta alla pagina originale...")
                                driver.get(original_url)
                                time.sleep(5)
                                if "challenge" not in driver.current_url:
                                    print("🎉 Navigazione diretta riuscita!")
                                    return True
                        except Exception as nav_err:
                            print(f"❌ Errore nella navigazione: {nav_err}")
                else:
                    print("❌ Impossibile applicare il token")
            else:
                print("❌ Nessun token ricevuto da Capsolver")
        
        except Exception as e:
            print(f"❌ Errore con la libreria capsolver: {e}")
            
            # Se la libreria capsolver fallisce, proviamo con l'API REST diretta
            print("🔄 Tentativo con API REST diretta...")
            return _bypass_with_rest_api(driver, api_key, current_url, site_key)
            
        return False
        
    except Exception as e:
        print(f"❌ Errore generale: {str(e)}")
        return False


# Funzione di supporto per utilizzare l'API REST direttamente
def _bypass_with_rest_api(driver, api_key, current_url, site_key):
    """Utilizza l'API REST di Capsolver quando la libreria fallisce"""
    try:
        # Prepara i dati per la richiesta
        task_payload = {
            "clientKey": api_key,
            "task": {
                "type": "AntiTurnstileTaskProxyLess",
                "websiteURL": current_url,
                "websiteKey": site_key
            }
        }
        
        print("📊 Payload richiesta:", json.dumps(task_payload, indent=2))
        
        # Ottieni il captcha
        headers = {'Content-Type': 'application/json'}
        
        # Step 1: Create task
        create_task_response = requests.post(
            'https://api.capsolver.com/createTask',
            json=task_payload,
            headers=headers
        )
        
        print(f"📨 Risposta: {create_task_response.status_code}")
        create_task_data = create_task_response.json()
        
        if 'errorId' in create_task_data and create_task_data['errorId'] > 0:
            print(f"❌ Errore API: {create_task_data.get('errorCode', 'Sconosciuto')} - {create_task_data.get('errorDescription', 'Nessun dettaglio')}")
            return False
        
        task_id = create_task_data.get('taskId')
        if not task_id:
            print("❌ Task ID non ricevuto")
            return False
        
        print(f"✅ Task creato (ID: {task_id})")
        
        # Step 2: Get task result
        max_attempts = 30
        for attempt in range(max_attempts):
            print(f"⏳ Attesa soluzione... Tentativo {attempt+1}/{max_attempts}")
            time.sleep(3)
            
            get_task_payload = {
                "clientKey": api_key,
                "taskId": task_id
            }
            
            get_result_response = requests.post(
                'https://api.capsolver.com/getTaskResult',
                json=get_task_payload,
                headers=headers
            )
            
            get_result_data = get_result_response.json()
            
            if get_result_data.get('status') == 'ready':
                token = get_result_data.get('solution', {}).get('token')
                if token:
                    print("✅ Token ricevuto!")
                    
                    # Applica token
                    success = driver.execute_script(f"""
                        try {{
                            // Imposta il token nei campi Turnstile
                            var tokenInputs = document.querySelectorAll('input[name="cf-turnstile-response"]');
                            if (tokenInputs.length > 0) {{
                                for (var i = 0; i < tokenInputs.length; i++) {{
                                    tokenInputs[i].value = "{token}";
                                }}
                                console.log("Token inserito nei campi input");
                            }}
                            
                            // Imposta il token come cookie
                            document.cookie = "cf_clearance={token}; path=/; domain=.toyscenter.it; secure";
                            console.log("Token impostato come cookie");
                            
                            return true;
                        }} catch(e) {{
                            console.error("Errore:", e);
                            return false;
                        }}
                    """)
                    
                    if success:
                        print("🚀 Token applicato, ricarico la pagina...")
                        # driver.refresh()
                        # time.sleep(5)
                        return True
                    else:
                        print("❌ Impossibile applicare il token")
                        return False
                    
                else:
                    print("❌ Token non trovato nella soluzione")
                    return False
            
            elif get_result_data.get('status') == 'failed':
                print(f"❌ Task fallito: {get_result_data.get('errorDescription', 'Errore sconosciuto')}")
                return False
        
        print("⌛ Tempo massimo di attesa superato")
        return False
        
    except Exception as e:
        print(f"❌ Errore nell'API REST: {str(e)}")
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