from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import string


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
    driver.find_element(By.XPATH, '//*[@id="billing.first_name"]').send_keys(random_string())
    driver.find_element(By.XPATH, '//*[@id="billing.last_name"]').send_keys(user_data["surname"])
    driver.find_element(By.XPATH, '//*[@id="billing.address_1"]').send_keys(random_string() + " " + user_data["address_line_1"][:-2])
    driver.find_element(By.XPATH, '//*[@id="billing.address_2"]').send_keys(user_data["address_line_1"][-2:])
    driver.find_element(By.XPATH, '//*[@id="billing.postcode"]').send_keys(user_data["zipcode"])
    driver.find_element(By.XPATH, '//*[@id="billing.city"]').send_keys(user_data["city"])
    dropdown = driver.find_element(By.CSS_SELECTOR, ".choices__inner")
    dropdown.click()
    time.sleep(1)
    option = driver.find_element(By.XPATH, f"//div[@class='choices__item choices__item--choice choices__item--selectable' and @data-value='{get_province_code(user_data['state'])}']")
    option.click()
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="billing.phone"]').send_keys(random_phone_number())
    driver.find_element(By.XPATH, '//*[@id="billing_email"]').send_keys(random_string() + user_data["email"][6:])
    
    next_button = driver.find_element(By.XPATH, '//*[@id="step_address_buttons"]/button')
    next_button.click()


def random_string():
    length = random.randint(5, 10)
    return ''.join(random.choices(string.ascii_letters, k=length))


def random_phone_number():
    return ''.join(random.choices(string.digits, k=10))


def get_province_code(province_name):
    """
    Convert a province name to its code.
    
    Args:
        province_name (str): The name of the province (e.g., 'Modena')
        
    Returns:
        str: The province code (e.g., 'MO')
    """
    province_map = {
        'Agrigento': 'AG', 'Alessandria': 'AL', 'Ancona': 'AN', 'Aosta': 'AO',
        'Arezzo': 'AR', 'Ascoli Piceno': 'AP', 'Asti': 'AT', 'Avellino': 'AV',
        'Bari': 'BA', 'Barletta-Andria-Trani': 'BT', 'Belluno': 'BL', 'Benevento': 'BN',
        'Bergamo': 'BG', 'Biella': 'BI', 'Bologna': 'BO', 'Bolzano': 'BZ',
        'Brescia': 'BS', 'Brindisi': 'BR', 'Cagliari': 'CA', 'Caltanissetta': 'CL',
        'Campobasso': 'CB', 'Caserta': 'CE', 'Catania': 'CT', 'Catanzaro': 'CZ',
        'Chieti': 'CH', 'Como': 'CO', 'Cosenza': 'CS', 'Cremona': 'CR',
        'Crotone': 'KR', 'Cuneo': 'CN', 'Enna': 'EN', 'Fermo': 'FM',
        'Ferrara': 'FE', 'Firenze': 'FI', 'Foggia': 'FG', 'Forlì-Cesena': 'FC',
        'Frosinone': 'FR', 'Genova': 'GE', 'Gorizia': 'GO', 'Grosseto': 'GR',
        'Imperia': 'IM', 'Isernia': 'IS', 'La Spezia': 'SP', "L'Aquila": 'AQ',
        'Latina': 'LT', 'Lecce': 'LE', 'Lecco': 'LC', 'Livorno': 'LI',
        'Lodi': 'LO', 'Lucca': 'LU', 'Macerata': 'MC', 'Mantova': 'MN',
        'Massa-Carrara': 'MS', 'Matera': 'MT', 'Messina': 'ME', 'Milano': 'MI',
        'Modena': 'MO', 'Monza e Brianza': 'MB', 'Napoli': 'NA', 'Novara': 'NO',
        'Nuoro': 'NU', 'Oristano': 'OR', 'Padova': 'PD', 'Palermo': 'PA',
        'Parma': 'PR', 'Pavia': 'PV', 'Perugia': 'PG', 'Pesaro e Urbino': 'PU',
        'Pescara': 'PE', 'Piacenza': 'PC', 'Pisa': 'PI', 'Pistoia': 'PT',
        'Pordenone': 'PN', 'Potenza': 'PZ', 'Prato': 'PO', 'Ragusa': 'RG',
        'Ravenna': 'RA', 'Reggio Calabria': 'RC', 'Reggio Emilia': 'RE', 'Rieti': 'RI',
        'Rimini': 'RN', 'Roma': 'RM', 'Rovigo': 'RO', 'Salerno': 'SA',
        'Sassari': 'SS', 'Savona': 'SV', 'Siena': 'SI', 'Siracusa': 'SR',
        'Sondrio': 'SO', 'Sud Sardegna': 'SU', 'Taranto': 'TA', 'Teramo': 'TE',
        'Terni': 'TR', 'Torino': 'TO', 'Trapani': 'TP', 'Trento': 'TN',
        'Treviso': 'TV', 'Trieste': 'TS', 'Udine': 'UD', 'Varese': 'VA',
        'Venezia': 'VE', 'Verbano-Cusio-Ossola': 'VB', 'Vercelli': 'VC', 'Verona': 'VR',
        'Vibo Valentia': 'VV', 'Vicenza': 'VI', 'Viterbo': 'VT'
    }
    
    return province_map.get(province_name, '')