import os
import requests
import schedule
import time
import random

TOKEN = "AAAAAAAAA"
CHAT_ID = 11111111

# List of random algo trading messages
messages = [
    "📈 Market Trend Alert: EMA & RSI crossover detected!",
    "📉 Stop-loss triggered on BTC/USD. Reviewing risk management strategy.",
    "🔔 New Signal: Buying opportunity in NIFTY 50 based on momentum analysis.",
    "⚡ High volatility detected! Adjusting risk exposure accordingly.",
    "📊 Backtest results show 85% win rate for the latest strategy. Live testing now!",
    "🚀 Options Straddle strategy deployed at ATM strike. Monitoring P&L.",
    "💰 Profit booking alert: Target hit for intraday trade on BANKNIFTY.",
    "🛑 Trade execution error! Investigating API response.",
    "🎯 Fibonacci retracement levels indicate a reversal zone approaching.",
    "🔄 Dynamic hedging activated based on delta-neutral strategy."
]

# Load environment variables
def send_telegram_message(token, id, message=None):
    """Sends a message to a Telegram chat."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": id,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print(f"Sent: {message} | Response: {response.json()}")
    return response.json()


def send_telegram_message1():
    """Sends a random algorithmic trading message to Telegram."""
    message = random.choice(messages)
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print(f"Sent: {message} | Response: {response.json()}")



# Example usage
if __name__ == "__main__":

    # Schedule the task every 3 minutes
    schedule.every(3).minutes.do(send_telegram_message1)

    # Run indefinitely
    print("✅ Algo trading message scheduler started...")
    while True:
        schedule.run_pending()
        time.sleep(1)



