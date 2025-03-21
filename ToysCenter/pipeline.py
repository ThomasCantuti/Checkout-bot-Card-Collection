import undetected_chromedriver as uc
import time
from dotenv import load_dotenv
import os
import json
import subprocess
import sys
import traceback
from monitor_notify import monitor_and_add_to_cart
from user_data_compiling import compiling_form
from payment import payment_and_confirmation

load_dotenv()
REFRESH_INTERVAL = 2
TOYS_CENTER_URL = os.environ.get('TOYS_CENTER_URL')
TOYS_CENTER_KEY = os.environ.get('TOYS_CENTER_KEY')
ROOT_PATH = os.environ.get('ROOT_PATH')
USER_PATH = os.path.join(ROOT_PATH, "Data", "alle.json")
USER_DATA = json.load(open(USER_PATH))

# Variabile per controllare il loop continuo
KEEP_RUNNING = True
# Tempo di attesa tra i tentativi di riavvio in caso di errore (in secondi)
RESTART_DELAY = 10

def prevent_sleep():
    """Impedisce al Mac di andare in sospensione durante l'esecuzione del bot"""
    # Esegue caffeinate in background per impedire la sospensione
    # -d impedisce al display di andare in sleep
    # -i impedisce al sistema di andare in idle sleep
    return subprocess.Popen(['caffeinate', '-d', '-i'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)

# ==========================
# Main Function
# ==========================
def run_bot():
    options = uc.ChromeOptions()
    driver = None
    
    try:
        driver = uc.Chrome(options=options)
        driver.implicitly_wait(5)

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
        
        # Se arriviamo qui, l'esecuzione è terminata con successo
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Stack trace:")
        traceback.print_exc()
        return False
    finally:
        if driver:
            time.sleep(5)
            driver.quit()

def main():
    # Avvia il processo per impedire la sospensione
    caffeinate_process = prevent_sleep()
    
    try:
        while KEEP_RUNNING:
            print(f"Avvio del bot: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            success = run_bot()
            
            if success:
                print("Il bot ha completato con successo l'acquisto!")
                # Se preferisci terminare dopo un acquisto riuscito, decommentare la linea seguente
                break
            
            print(f"Riavvio del bot tra {RESTART_DELAY} secondi...")
            time.sleep(RESTART_DELAY)
    
    except KeyboardInterrupt:
        print("Interruzione manuale del bot")
    finally:
        # Termina il processo caffeinate quando il programma termina
        if caffeinate_process:
            caffeinate_process.terminate()
            print("Processo anti-sospensione terminato")


if __name__ == "__main__":
    main()