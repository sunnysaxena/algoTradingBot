# AlgoTradingBot 🚀

## 🔹 Overview
AlgoTradingBot is an automated trading system that executes trades based on predefined strategies. 
It integrates with multiple brokers, fetches real-time market data, and supports advanced trading features like **options trading, risk management, and live monitoring.**

## 🔹 Features

✅ Modular broker integration (Fyers, Zerodha, etc.)

✅ Live market data streaming via WebSockets

✅ Options trading strategies (Straddle, Strangle, etc.)

✅ EMA & RSI crossover strategy for automated trading

✅ Risk management (Stop-loss, Target, Trailing SL)

✅ Dynamic strike price selection from the option chain

✅ Multi-threaded execution for high-speed trading

✅ Encrypted credential storage for security

✅ Real-time alerts via Telegram


### ⚙️ Installation
1️⃣ Clone the Repository

    git clone https://github.com/yourusername/AlgoTradingBot.git
    cd AlgoTradingBot

2️⃣ Set Up a Virtual Environment (Recommended)

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3️⃣ Install Dependencies

    pip install -r requirements.txt

4️⃣ Configure Environment Variables

Create a .env file and add your broker credentials:

    BROKER=Fyers
    API_KEY=your_api_key
    API_SECRET=your_api_secret
    ACCESS_TOKEN=your_access_token
    LOG_PATH=logs/

5️⃣ Start the Bot

    python main.py

### 🛠️ Supported Brokers

✅ Fyers

✅ Zerodha (Coming soon...)

✅ AngelOne (Coming soon...)


### 📡 Web UI for Monitoring

A React-based UI is available to:

✅ View live market data 📈

✅ Monitor orders and positions 🔍

✅ Configure and modify strategies ⚙️

### 📝 Logging & Error Handling
* All logs are stored in the logs/ directory
* Errors are automatically logged for debugging
