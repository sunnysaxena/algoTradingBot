import requests


class OptionChain:
    """
    Fetches and processes option chain data from a broker API.
    """

    def __init__(self, broker_api):
        """
        Initialize OptionChain with a broker API instance.

        :param broker_api: Broker API client for fetching option chain data.
        """
        self.broker_api = broker_api

    def fetch_option_chain(self, symbol):
        """
        Retrieve the option chain for a given symbol.

        :param symbol: Stock symbol for which to fetch options data.
        :return: Dictionary containing option chain data.
        """
        try:
            return self.broker_api.get_option_chain(symbol)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching option chain: {e}")
            return None

    def filter_strikes(self, option_chain, strike_range):
        """
        Filter option strikes within a given range.

        :param option_chain: Full option chain data.
        :param strike_range: Tuple containing min and max strike price.
        :return: Filtered option chain data.
        """
        min_strike, max_strike = strike_range
        return [option for option in option_chain if min_strike <= option['strike'] <= max_strike]
