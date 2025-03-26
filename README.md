# Checkout Bot Card Collection
An automated bot for monitoring and purchasing collectible cards from e-commerce sites, with a specific focus on ToysCenter.it.

## 📋 Overview
This project implements an automated bot capable of:

- Monitoring the availability of specific products
- Automatically solving Cloudflare captchas
- Filling forms with user data
- Managing the payment process
- Running multiple instances simultaneously (multi-threading)

The bot is particularly useful for acquiring collectible cards or other limited availability products that tend to sell out quickly.

## 🧩 Project Structure
```plaintext
Checkout-bot-Card-Collection/
├── ToysCenter/
│   ├── monitoring.py      # Product monitoring
│   ├── user_data_compiling.py  # User form filling
│   ├── payment.py         # Payment process management
│   ├── pipeline.py        # Coordination of the entire process
├── Utility/
│   └── utils.py           # Utility functions (captcha solver, etc.)
├── tasks/
│   └── toyscenter.csv     # CSV file with details of products to monitor
├── .env                   # Environment variables
└── settings.json          # General settings
```

## 🔧 Requirements
Python 3.8+  
Chrome Browser  
Stable internet connection  
Account for captcha resolution (CapSolver)

## 📦 Dependencies
selenium  
undetected_chromedriver  
curl_cffi  
python-dotenv

## ⚙️ Configuration
1. Clone the repository:
```bash
git clone https://github.com/tuousername/Checkout-bot-Card-Collection.git
cd Checkout-bot-Card-Collection
```

2. Install the dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the environment variables:
```
ROOT_PATH=/path/to/your/project
TOYS_CENTER_KEY=0x4AAAAAAA_slGZ9sK4UREXX
```

4. Configure `settings.json` with your CapSolver API key:
```json
{
    "CAPSOLVER_API_KEY": "YOUR_API_KEY"
}
```

5. Configure the details of the products to monitor in `tasks/toyscenter.csv` and the data.

## 🚀 Usage
Run the main pipeline:
```bash
python ToysCenter/pipeline.py
```

## 🔄 Operating Process
1. Monitoring: The bot periodically checks the availability of the specified product.
2. Add to cart: When the product becomes available, it is added to the cart.
3. Data filling: User data is automatically filled in the forms.
4. Payment: Payment data is entered and the transaction is completed.
5. Confirmation: The bot waits for order confirmation.

## 🧵 Threading Functionality
The bot implements an advanced multi-threading system that allows:

- Monitoring multiple sites or products simultaneously
- Configuring the maximum number of simultaneous threads (default: 10)
- Automatically managing thread startup and termination
- Coordinating parallel purchase operations on different products
- Automatically restarting the process in case of errors

Each row in the task CSV file is executed in a separate thread, allowing you to monitor and purchase multiple products from different sites simultaneously, thus maximizing the chances of success during limited product launches.

## ⚠️ Legal Notes
This project was created for educational purposes only. The use of bots for automated purchases may violate the terms of service of some websites. The author assumes no responsibility for any violations or consequences arising from the use of this software.