import os
import time
import yaml
import pandas as pd
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
from trade_utils.utils import TIME_ZONE

from utils.env_loader import load_env
from utils.config_loader import load_config
from broker.broker_factory import BrokerFactory
from database.timescale_handler import TimescaleDBHandler

# Load environment variables
load_dotenv(load_env())
config_path = load_config()

# Load broker from config.yml
with (open(config_path, "r") as file):
    config = yaml.safe_load(file)

broker = BrokerFactory.get_broker()

fyers_symbols = config['trading_symbols']['fyers']


def get_database_handler():
    """
    Initializes and returns a DatabaseHandler instance for the specified database type.
    """
    return TimescaleDBHandler()


today_date = datetime.today().strftime("%Y-%m-%d")


def get_table_last_timestamps():
    query = """
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema IN ('fno', 'fno');
    """

    table_date_time = {}
    old_date_time = {}

    with TimescaleDBHandler() as handler:  # Using the context manager
        result = handler.execute_query(query)
        all_tables = [(schema, table) for schema, table in result if table.endswith('_1m') or table.endswith('_1m')]

        for schema, table_name in all_tables:
            full_table_name = f"{schema}.{table_name}"
            query = f"SELECT * FROM {full_table_name} ORDER BY timestamp DESC LIMIT 1;"
            table_data = handler.execute_query(query)

            if not table_data:
                continue  # Skip empty tables

            last_row = table_data[0]
            last_date = last_row[0]  # Assuming timestamp is in the second column

            if isinstance(last_date, float):
                # Convert epoch timestamp to datetime
                last_date = datetime.fromtimestamp(last_date)
                print(last_date)
                exit()
            elif isinstance(last_date, str):
                # Convert string timestamp to datetime
                last_date = datetime.strptime(last_date.split('+')[0], '%Y-%m-%d %H:%M:%S')
                print(last_date)
                exit()

            old_date_time[full_table_name] = last_date.strftime("%Y-%m-%d")

            # Next day's date
            table_date_time[full_table_name] = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
    return table_date_time


def update_all_tables_fyers():
    """
    Updates all tables with missing data from Fyers API.
    """
    for full_table_name, last_date in get_table_last_timestamps().items():
        schema, table_name = full_table_name.split(".")  # Extract schema & table name

        print(f"Table Name : {table_name} === Last Date : {last_date} === Today's Date {today_date}")

        if last_date == today_date:
            print(f"{table_name} is already up to date.")
            continue

        dates = pd.date_range(start=last_date, end=today_date).tolist()
        master_data = []

        # ✅ Fix: Correcting symbol mapping
        if table_name in ['nifty50_1m']:
            symbol = fyers_symbols['NIFTY50']
        elif table_name in ['sensex_1m']:
            symbol = fyers_symbols['SENSEX']
        else:
            print(f'⚠️ Invalid symbol name: "{table_name}"')
            continue  # Skip this table if the symbol is not found

        for range_from, range_to in zip(dates, dates[1:]):
            data = {
                "symbol": symbol,
                "resolution": "1",
                "date_format": "1",
                "range_from": range_from.strftime("%Y-%m-%d"),
                "range_to": range_to.strftime("%Y-%m-%d"),
                "cont_flag": "1"
            }

            response = broker.history(data=data)

            # ✅ Fix: Debug response to check if 'candles' exists
            if 'candles' not in response:
                print(f"⚠️ API response missing 'candles' key for {symbol}: {response}")
                continue  # Skip this date range

            master_data += response['candles']

        # ✅ Ensure master_data is not empty before processing
        if master_data:
            df = pd.DataFrame(master_data, columns=["epoc", "open", "high", "low", "close", "volume"])
            df['timestamp'] = pd.to_datetime(df['epoc'], unit='s', utc=True).map(lambda x: x.tz_convert(TIME_ZONE))
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')
            df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            df = df[["timestamp", "open", "high", "low", "close", "volume"]]
            df.drop_duplicates(inplace=True)
            df.sort_values(by='timestamp', inplace=True)
            df['volume'] = 0

            print(df.head())
            print(df.tail())

            if not df.empty:
                with TimescaleDBHandler() as db_handler:
                    try:
                        # Batch insert in chunks to optimize performance
                        batch_size = 1000  # Customize as needed
                        insert_query = f"""
                            INSERT INTO {schema}.{table_name} (timestamp, open, high, low, close, volume) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (timestamp) DO NOTHING;
                        """
                        for i in range(0, len(df), batch_size):
                            batch = df.iloc[i:i + batch_size].values.tolist()
                            db_handler.cursor.executemany(insert_query, batch)
                            db_handler.conn.commit()
                            print(f"✅ Inserted {len(batch)} rows into {full_table_name}")
                    except Exception as e:
                        db_handler.conn.rollback()
                        print(f"❌ Error inserting data into {full_table_name}: {e}")
            else:
                print(f"⚠️ No new data available for {table_name}.")


# Prompt user for update
ask = input("Do you want to update 1-min data? (Y/n): ")

if ask.lower() == 'y':
    update_all_tables_fyers()
