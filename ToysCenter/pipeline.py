import undetected_chromedriver as uc
import time
from dotenv import load_dotenv
import os
import csv
import subprocess
import sys
import traceback
import threading
from monitoring import monitor_and_add_to_cart
from user_data_compiling import compiling_form
from payment import payment_and_confirmation

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Carica tutte le righe del CSV in una lista
with open(os.path.join(project_root, "tasks", "toyscenter.csv"), "r", encoding="utf-8") as csv_file:
    USER_DATA_ROWS = list(csv.DictReader(csv_file))

load_dotenv()
REFRESH_INTERVAL = 2
TOYS_CENTER_KEY = os.environ.get('TOYS_CENTER_KEY')

# Variabile per controllare il loop continuo
KEEP_RUNNING = True
# Tempo di attesa tra i tentativi di riavvio in caso di errore (in secondi)
RESTART_DELAY = 10
# Numero massimo di thread da eseguire contemporaneamente
MAX_THREADS = 10
# Lock per la sincronizzazione degli output su console
console_lock = threading.Lock()

def prevent_sleep():
    """Prevents the system from sleeping during bot execution, works on both macOS and Windows"""
    if sys.platform == "darwin":  # macOS
        # Use caffeinate to prevent sleep
        # -d prevents display sleep
        # -i prevents idle sleep
        return subprocess.Popen(['caffeinate', '-d', '-i'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
    elif sys.platform == "win32":  # Windows
        try:
            # For Windows, simulate minimal mouse movement every 59 seconds
            cmd = [sys.executable, '-c', 
                  'import ctypes, time; while True: ctypes.windll.user32.mouse_event(0x0001, 0, 0, 0, 0); time.sleep(0.1); ctypes.windll.user32.mouse_event(0x0001, 0, 0, 0, 0); time.sleep(59)']
            
            # Start process without showing console window
            startupinfo = None
            if hasattr(subprocess, 'STARTUPINFO'):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            return subprocess.Popen(cmd, 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   startupinfo=startupinfo)
        except Exception as e:
            print(f"Warning: Could not prevent Windows from sleeping: {e}")
            return None
    else:
        print(f"Warning: Sleep prevention not implemented for {sys.platform}")
        return None

# ==========================
# Main Function
# ==========================
def run_bot(user_data_row, thread_id):
    """Esegue un'istanza del bot con una specifica riga di dati utente"""
    options = uc.ChromeOptions()
    # options.add_argument("--headless")
    driver = None
    
    try:
        driver = uc.Chrome(options=options)

        # 1. MONITORING
        with console_lock:
            print(f"[Thread {thread_id}] Starting monitoring... URL: {user_data_row['product_link']}")
        
        # Usa il link specifico dal CSV per questo thread
        monitor_and_add_to_cart(driver, user_data_row['product_link'], TOYS_CENTER_KEY)
        
        with console_lock:
            print(f"[Thread {thread_id}] End of monitoring")

        # 2. AUTOMATIC FORM FILLING & CHECKOUT
        with console_lock:
            print(f"[Thread {thread_id}] Starting automatic compilation...")
        compiling_form(driver, user_data_row)
        with console_lock:
            print(f"[Thread {thread_id}] End of automatic compilation")

        # 3. PAYMENT
        with console_lock:
            print(f"[Thread {thread_id}] Starting payment...")
        payment_and_confirmation(driver, user_data_row)
        with console_lock:
            print(f"[Thread {thread_id}] End of payment")

        time.sleep(5)
        with console_lock:
            print(f"[Thread {thread_id}] Procedure completed!")
        
        # Se arriviamo qui, l'esecuzione è terminata con successo
        return True

    except Exception as e:
        with console_lock:
            print(f"[Thread {thread_id}] An error occurred: {e}")
            print(f"[Thread {thread_id}] Stack trace:")
            traceback.print_exc()
        return False
    finally:
        if driver:
            time.sleep(5)
            driver.quit()

def bot_thread_function(user_data_row, thread_id):
    """Funzione che gestisce un singolo thread del bot"""
    try:
        while KEEP_RUNNING:
            with console_lock:
                print(f"[Thread {thread_id}] Avvio del bot: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            success = run_bot(user_data_row, thread_id)
            
            if success:
                with console_lock:
                    print(f"[Thread {thread_id}] Il bot ha completato con successo l'acquisto!")
                # Possiamo terminare il thread dopo un acquisto riuscito
                break
            
            with console_lock:
                print(f"[Thread {thread_id}] Riavvio del bot tra {RESTART_DELAY} secondi...")
            time.sleep(RESTART_DELAY)
    
    except Exception as e:
        with console_lock:
            print(f"[Thread {thread_id}] Errore nel thread: {e}")
            traceback.print_exc()

def main():
    # Avvia il processo per impedire la sospensione
    caffeinate_process = prevent_sleep()
    threads = []
    
    try:
        # Crea un thread per ogni riga di dati utente
        for i, user_data_row in enumerate(USER_DATA_ROWS):
            # Limita il numero di thread attivi
            while len([t for t in threads if t.is_alive()]) >= MAX_THREADS:
                time.sleep(1)  # Aspetta che un thread termini
            
            # Crea e avvia un nuovo thread
            thread = threading.Thread(
                target=bot_thread_function,
                args=(user_data_row, i+1),
                name=f"BotThread-{i+1}"
            )
            threads.append(thread)
            thread.start()
            
            print(f"Avviato thread {i+1} per prodotto: {user_data_row['product_link']}")
            
            # Piccola pausa tra l'avvio di thread consecutivi
            time.sleep(2)
        
        # Attendi che tutti i thread terminino
        for thread in threads:
            thread.join()
            
    except KeyboardInterrupt:
        print("\nInterruzione manuale del programma")
        # Imposta la variabile globale per terminare i cicli while nei thread
        global KEEP_RUNNING
        KEEP_RUNNING = False
        
        # Attendi che tutti i thread terminino
        print("In attesa che tutti i thread terminino...")
        for thread in threads:
            thread.join()
    finally:
        # Termina il processo caffeinate quando il programma termina
        if caffeinate_process:
            caffeinate_process.terminate()
            print("Processo anti-sospensione terminato")


if __name__ == "__main__":
    main()