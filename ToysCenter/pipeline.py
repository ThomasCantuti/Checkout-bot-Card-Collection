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
# Load all CSV rows into a list
with open(os.path.join(project_root, "tasks", "toyscenter.csv"), "r", encoding="utf-8") as csv_file:
    USER_DATA_ROWS = list(csv.DictReader(csv_file))

load_dotenv()
REFRESH_INTERVAL = 2
TOYS_CENTER_KEY = os.environ.get('TOYS_CENTER_KEY')

# Variable to control the continuous loop
KEEP_RUNNING = True
# Wait time between restart attempts in case of error (in seconds)
RESTART_DELAY = 10
# Maximum number of threads to run simultaneously
MAX_THREADS = 10
# Lock for console output synchronization
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
    """Runs a bot instance with specific user data row"""
    options = uc.ChromeOptions()
    # options.add_argument("--headless")
    driver = None
    
    try:
        driver = uc.Chrome(options=options)

        # 1. MONITORING
        with console_lock:
            print(f"[Thread {thread_id}] Starting monitoring... URL: {user_data_row['product_link']}")
        
        # Use the specific link from CSV for this thread
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
        
        # If we get here, execution completed successfully
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
    """Function that manages a single bot thread"""
    try:
        while KEEP_RUNNING:
            with console_lock:
                print(f"[Thread {thread_id}] Bot starting: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            success = run_bot(user_data_row, thread_id)
            
            if success:
                with console_lock:
                    print(f"[Thread {thread_id}] The bot has successfully completed the purchase!")
                # We can terminate the thread after a successful purchase
                break
            
            with console_lock:
                print(f"[Thread {thread_id}] Restarting bot in {RESTART_DELAY} seconds...")
            time.sleep(RESTART_DELAY)
    
    except Exception as e:
        with console_lock:
            print(f"[Thread {thread_id}] Error in thread: {e}")
            traceback.print_exc()

def main():
    # Start the process to prevent system sleep
    caffeinate_process = prevent_sleep()
    threads = []
    
    try:
        # Create a thread for each user data row
        for i, user_data_row in enumerate(USER_DATA_ROWS):
            # Limit the number of active threads
            while len([t for t in threads if t.is_alive()]) >= MAX_THREADS:
                time.sleep(1)  # Wait for a thread to terminate
            
            # Create and start a new thread
            thread = threading.Thread(
                target=bot_thread_function,
                args=(user_data_row, i+1),
                name=f"BotThread-{i+1}"
            )
            threads.append(thread)
            thread.start()
            
            print(f"Started thread {i+1} for product: {user_data_row['product_link']}")
            
            # Small pause between starting consecutive threads
            time.sleep(2)
        
        # Wait for all threads to terminate
        for thread in threads:
            thread.join()
            
    except KeyboardInterrupt:
        print("\nManual program interruption")
        # Set the global variable to end while loops in threads
        global KEEP_RUNNING
        KEEP_RUNNING = False
        
        # Wait for all threads to terminate
        print("Waiting for all threads to terminate...")
        for thread in threads:
            thread.join()
    finally:
        # Terminate the caffeinate process when the program ends
        if caffeinate_process:
            caffeinate_process.terminate()
            print("Anti-suspension process terminated")


if __name__ == "__main__":
    main()