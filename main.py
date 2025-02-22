"""
The main.py file serves as the entry point for your algorithmic trading system.
It initializes and orchestrates the different components, such as data fetching,
strategy execution, order placement, and monitoring.

main.py Purpose
✅ Loads configurations (database, broker API, Redis, etc.)
✅ Initializes components (WebSockets, caching, logging, and strategies)
✅ Starts market data streaming
✅ Runs trading strategies (e.g., EMA & RSI crossover)
✅ Executes and manages orders
✅ Monitors open positions & sends alerts

"""

import threading
import time
import yaml
from core.data_fetcher import DataFetcher
from core.signal_generator import SignalGenerator
from core.order_execution import OrderExecution
from websocket.websocket_handler import WebSocketHandler
from monitoring.alerts import Alerts
from core.cache import Cache

# Load configuration
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize components
data_fetcher = DataFetcher()
signal_generator = SignalGenerator()
order_executor = OrderExecution()
websocket_handler = WebSocketHandler()
alerts = Alerts()
cache = Cache()

# Symbols to track
symbols = ["NSE:NIFTY50-INDEX", "NSE:RELIANCE", "NSE:TCS"]

def run_trading_loop():
    """Main trading loop: Fetch data, generate signals, and execute trades."""
    while True:
        try:
            for symbol in symbols:
                # Fetch live OHLC data
                ohlc_data = data_fetcher.fetch_latest_ohlc(symbol)
                cache.set_cache(f"ohlc:{symbol}", ohlc_data, expiry=60)

                # Generate trade signals
                trade_signal = signal_generator.get_trade_signal(symbol, ohlc_data)

                # Execute orders based on signals
                if trade_signal:
                    order_response = order_executor.execute_order(trade_signal)
                    alerts.send_alert(f"Trade executed: {order_response}")

            time.sleep(5)  # Control loop frequency
        except Exception as e:
            alerts.send_alert(f"Error in trading loop: {e}")

# Start WebSocket in a separate thread
websocket_thread = threading.Thread(target=websocket_handler.start_stream, daemon=True)
websocket_thread.start()

# Start main trading loop
run_trading_loop()
