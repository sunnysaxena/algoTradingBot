import os
import yaml
import pandas as pd
import pandas_ta as ta
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dotenv import load_dotenv
from strategies.ema_rsi_crossover import EMA_RSI_CrossoverStrategy

# Load the .env and config.yml file explicitly from config/
ROOT_DIR = Path(__file__).resolve().parent.parent  # Get root directory
config_path = os.path.join(ROOT_DIR, "config/config.yaml")
env_path = os.path.join(ROOT_DIR, "config/.env")

# Load environment variables
load_dotenv(env_path)

# Load config.yml
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

# Database Connection
DB_HOST = os.getenv("MYSQL_HOST")
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = config["database"]["mysql"]["name"]
DB_TABLE = config['database']['mysql']['historical_data_table']

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

# Load Historical Data
def load_historical_data():
    query = f"SELECT timestamp, open, high, low, close, volume FROM {DB_TABLE} LIMIT 365"
    df = pd.read_sql(query, engine, parse_dates=["timestamp"])
    df.set_index("timestamp", inplace=True)
    return df

# Main Execution
def run_backtest():
    active_strategy = config["trading"]["active_strategy"]
    strategy_params = config["trading"]["strategies"][active_strategy]

    print(f"\n🚀 Running Backtest for {active_strategy}...")

    df = load_historical_data()

    # Select strategy dynamically
    if active_strategy == "EMA_RSI_Crossover":
        strategy = EMA_RSI_CrossoverStrategy(df, strategy_params)
    else:
        raise ValueError("Unsupported strategy in config!")

    strategy.apply_strategy()
    results = strategy.backtest()
    strategy.plot_results()

# Run Backtest
run_backtest()
