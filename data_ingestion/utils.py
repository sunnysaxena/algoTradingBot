"""
Brief Overview of Each File:

1. fetch_ohlc.py

    Fetch historical OHLC data from API (Yahoo Finance, Broker API, etc.).
    Process and format the data before storing.

2. store_timescale.py

    Connects to TimescaleDB and stores OHLC data.
    Ensures indexing, hypertables, and efficient query performance.

3. realtime_ingestion.py

    Handles WebSocket-based real-time market data streaming.
    Stores real-time data in TimescaleDB.
4. __init__.py

    Makes data_ingestion a Python package.
    Can contain initialization logic if needed.

5. config.py (Optional)
    Stores environment variables and API credentials.

6. utils.py (Optional)
    Contains common functions like timestamp conversion, logging, etc.

Example Usage
You can import and use these modules in your main algorithmic trading script:

    from data_ingestion.fetch_ohlc import fetch_historical_data
    from data_ingestion.store_timescale import store_to_timescale
    from data_ingestion.realtime_ingestion import stream_market_data

    # Fetch historical data
    ohlc_data = fetch_historical_data(symbol="NIFTY50", interval="1d")

    # Store in TimescaleDB
    store_to_timescale(ohlc_data)

    # Stream live data
    stream_market_data()

"""


# data_ingestion/utils.py
from datetime import datetime
import pytz

def convert_utc_to_ist(timestamp):
    """Convert UTC timestamp to IST."""
    utc_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    ist_time = utc_time.astimezone(pytz.timezone("Asia/Kolkata"))
    return ist_time.strftime("%Y-%m-%d %H:%M:%S")
