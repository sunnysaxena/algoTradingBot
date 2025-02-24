import os
import webbrowser
from dotenv import load_dotenv
from fyers_apiv3 import fyersModel

# Get the absolute path of the credentials.ini file
env_path = os.path.join(os.path.dirname(__file__), 'config/.env')

# Load environment variables
load_dotenv(dotenv_path=env_path)

# Use environment variables for credentials
FYERS_CLIENT_ID = os.getenv('FYERS_CLIENT_ID')
FYERS_SECRET_KEY = os.getenv('FYERS_SECRET_KEY')
FYERS_REDIRECT_URL = os.getenv('FYERS_REDIRECT_URL')
FYERS_RESPONSE_TYPE = os.getenv('FYERS_RESPONSE_TYPE')
FYERS_GRANT_TYPE = os.getenv('FYERS_GRANT_TYPE')
FYERS_ACCESS_TOKEN = os.getenv('FYERS_ACCESS_TOKEN')
print(FYERS_ACCESS_TOKEN)


def generate_access_token():
    session = fyersModel.SessionModel(
        client_id=FYERS_CLIENT_ID,
        secret_key=FYERS_SECRET_KEY,
        redirect_uri=FYERS_REDIRECT_URL,
        response_type=FYERS_RESPONSE_TYPE,
        grant_type=FYERS_GRANT_TYPE
    )

    response = session.generate_authcode()
    print("Login Url : ", response)

    # This command is used to open the url in default system browser
    webbrowser.open(response, new=1)

    auth_code = input("Auth Code : ")

    session.set_token(auth_code)
    access_token = session.generate_token()['access_token']

    if os.path.exists(FYERS_ACCESS_TOKEN):
        os.remove(FYERS_ACCESS_TOKEN)

    with open(FYERS_ACCESS_TOKEN, 'w') as f:
        f.write(access_token)


if __name__ == '__main__':
    generate_access_token()
