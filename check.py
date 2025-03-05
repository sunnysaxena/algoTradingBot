import os
from dotenv import load_dotenv
from utils.env_loader import load_env

# Load environment variables
load_dotenv(load_env())

host = os.getenv("TIMESCALEDB_HOST")
user = os.getenv("TIMESCALEDB_USER")
password = os.getenv("TIMESCALEDB_PASSWORD")
database= os.getenv("TIMESCALEDB_DATABASE")


print(host, user, password, database)