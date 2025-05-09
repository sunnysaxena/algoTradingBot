import os
import webbrowser
import time
import logging
from flask import Flask, request
from threading import Thread
from dotenv import load_dotenv
from fyers_apiv3 import fyersModel

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), 'config/.env')
if not os.path.exists(env_path):
    logging.error("⚠️  .env file not found at: %s", env_path)
    raise FileNotFoundError(f".env file not found at: {env_path}")

load_dotenv(dotenv_path=env_path)

# Fetch credentials from environment variables
FYERS_CLIENT_ID = os.getenv('FYERS_CLIENT_ID')
FYERS_SECRET_KEY = os.getenv('FYERS_SECRET_KEY')
FYERS_REDIRECT_URL = os.getenv('FYERS_REDIRECT_URL')
FYERS_RESPONSE_TYPE = os.getenv('FYERS_RESPONSE_TYPE', 'code')
FYERS_GRANT_TYPE = os.getenv('FYERS_GRANT_TYPE', 'authorization_code')
FYERS_ACCESS_TOKEN_FILE = os.getenv('FYERS_ACCESS_TOKEN')

# Validate required credentials
required_vars = {
    "FYERS_CLIENT_ID": FYERS_CLIENT_ID,
    "FYERS_SECRET_KEY": FYERS_SECRET_KEY,
    "FYERS_REDIRECT_URL": FYERS_REDIRECT_URL,
    "FYERS_ACCESS_TOKEN_FILE": FYERS_ACCESS_TOKEN_FILE
}

for key, value in required_vars.items():
    if not value:
        logging.error(f"⚠️  Missing required environment variable: {key}")
        raise ValueError(f"Missing required environment variable: {key}")

logging.info("✅ Environment variables loaded successfully.")

# Flask app to capture auth_code
app = Flask(__name__)
auth_code = None  # Global variable to store auth_code

@app.route('/fyers/callback')
def callback():
    global auth_code
    auth_code = request.args.get('auth_code')

    if auth_code:
        logging.info(f"✅ Auth Code Received: {auth_code}")
        return """
        <html>
        <body>
            <h2>✅ Auth Code Received. Closing window...</h2>
            <script>
                setTimeout(() => { window.close(); }, 2000);
            </script>
        </body>
        </html>
        """
    else:
        logging.error("⚠️  Auth Code Not Found in Request.")
        return "Error: Auth Code Not Found."

def start_flask():
    app.run(port=5000, debug=False)

def generate_access_token():
    global auth_code

    # Start Flask server in a separate thread
    thread = Thread(target=start_flask, daemon=True)
    thread.start()

    # Initialize Fyers session
    session = fyersModel.SessionModel(
        client_id=FYERS_CLIENT_ID,
        secret_key=FYERS_SECRET_KEY,
        redirect_uri=FYERS_REDIRECT_URL,
        response_type=FYERS_RESPONSE_TYPE,
        grant_type=FYERS_GRANT_TYPE
    )

    # Generate authentication URL
    response = session.generate_authcode()
    if "https" not in response:
        logging.error("⚠️  Failed to generate authentication URL: %s", response)
        raise ValueError(f"Invalid response from Fyers API: {response}")

    logging.info("🔗 Login URL: %s", response)

    # Open the login URL (only once)
    try:
        webbrowser.open(response, new=1)
    except Exception as e:
        logging.warning("⚠️  Failed to open the browser: %s", e)

    # Wait for auth_code from Flask
    while auth_code is None:
        logging.info("⌛ Waiting for auth_code from Fyers...")
        time.sleep(1)

    # Exchange auth_code for access_token
    session.set_token(auth_code)
    token_response = session.generate_token()

    if 'access_token' not in token_response:
        logging.error("⚠️  Failed to generate access token: %s", token_response)
        raise ValueError("Access token generation failed.")

    access_token = token_response['access_token']
    logging.info("✅ Access token successfully generated.")

    # Save access token to file
    try:
        if os.path.exists(FYERS_ACCESS_TOKEN_FILE):
            os.remove(FYERS_ACCESS_TOKEN_FILE)

        with open(FYERS_ACCESS_TOKEN_FILE, 'w') as f:
            f.write(access_token)

        logging.info("🔐 Access token saved to: %s", FYERS_ACCESS_TOKEN_FILE)

    except Exception as e:
        logging.error("⚠️  Failed to save access token: %s", e)
        raise

if __name__ == '__main__':
    generate_access_token()
