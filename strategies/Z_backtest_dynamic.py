import os
import yaml
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlalchemy import create_engine

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
# URL-encode the password
DB_PASSWORD = quote_plus(DB_PASSWORD)
DB_NAME = config["database"]["mysql"]["name"]
DB_TABLE = config['database']['mysql']['tables']['nifty50_1d']

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
    library_name = config["trading"]["library"]["name"]
    strategy_params = config["trading"]["strategies"][active_strategy]

    print(f"\n🚀 Running Backtest for {active_strategy}...")

    df = load_historical_data()

    # Import strategy dynamically
    strategy_module = __import__(f"strategies.{active_strategy.lower()}", fromlist=[f"{active_strategy}Strategy"])
    StrategyClass = getattr(strategy_module, f"{active_strategy}Strategy")

    print(f'Active Strategy : {active_strategy}')
    print(f'Strategy Module : {strategy_module}')
    print(f'Strategy Class : {StrategyClass}')
    print(f'Strategy Params : {strategy_params}')
    print(f'Library Name : {library_name}')


    # Run Backtest
    strategy = StrategyClass(df, strategy_params, library_name)
    strategy.apply_strategy()
    results = strategy.backtest()
    strategy.plot_results()

# Run Backtest
run_backtest()
