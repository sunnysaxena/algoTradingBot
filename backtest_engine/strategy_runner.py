import pandas as pd
from trade_utils import timeframe_converter as converter
from trade_utils.data_resampler import convert_1min_to_timeframe
from utils.logger import get_logger  # Import get_logger

logger = get_logger(__name__)  # Get logger for this module


class StrategyRunner:
    """
    Runs a given trading strategy on historical data and generates trades.
    """

    def __init__(self, strategy_class, strategy_params, db_handler, initial_capital=1000000):
        """
        Initializes the StrategyRunner.

        Args:
            strategy_class (type): The class of the trading strategy.
            strategy_params (dict): Parameters for the strategy.
            db_handler (DatabaseHandler): An instance of the database handler.
            initial_capital (float, optional): The initial capital for the backtest. Defaults to 1000000.
        """
        self.strategy_class = strategy_class
        self.strategy_params = strategy_params
        self.db_handler = db_handler
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trades = []
        self.positions = {}  # To track open positions
        self.strategy_instance = None

    async def _fetch_historical_data(self, symbol, start_date, end_date, timeframe='1m', custom_table_name=None):
        """
        Fetches historical data for a given symbol and time range.

        Args:
            symbol (str): The trading symbol.
            start_date (str): The start date for historical data.
            end_date (str): The end date for historical data.
            timeframe (str): The timeframe for the data (e.g., '1m', '1d').
            custom_table_name (str, optional): The specific table name to use.

        Returns:
            pd.DataFrame: Historical data with columns like 'timestamp', 'open', 'high', 'low', 'close', 'volume'.
                          Returns an empty DataFrame if no data is found or an error occurs.
        """
        try:
            table_name = custom_table_name
            if not table_name:
                table_name = self.db_handler.get_table_name(symbol, timeframe)
                if not table_name:
                    logger.warning(f"No table mapping found for symbol '{symbol}' and timeframe '{timeframe}'.")
                    return pd.DataFrame()

            # Prepend the schema name to the table name
            full_table_name = f"fno.{table_name}"

            query = f"SELECT timestamp, open, high, low, close, volume FROM {full_table_name} WHERE timestamp >= '{start_date}' AND timestamp <= '{end_date}' ORDER BY timestamp ASC"
            # print(query)
            data = await self.db_handler.execute_query(query)
            if data:
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

                # Convert the timestamp column to Asia/Kolkata
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'],
                                                     utc=True)  # ensure that pandas knows that the column is in UTC.
                    df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')
                    df['timestamp'] = df['timestamp'].dt.tz_localize(None)
                else:
                    logger.warning("Timestamp column not found in DataFrame.")

                if timeframe == '1m':
                    df = df
                elif timeframe == '5m':
                    df = convert_1min_to_timeframe(df, '5T')
                elif timeframe == '15m':
                    df = convert_1min_to_timeframe(df, '15T')
                elif timeframe == '1h':
                    df = convert_1min_to_timeframe(df, '1H')
                elif timeframe == '1d':
                    df = convert_1min_to_timeframe(df, '1D')
                else:
                    df.set_index('timestamp', inplace=True)
                    df.index = pd.to_datetime(df.index)

                df.reset_index(inplace=True)
                df.set_index('timestamp', inplace=True)
                # print(df.columns)
                # print(df.shape)

                return df
            else:
                logger.info(
                    f"No historical data found for {symbol} between {start_date} and {end_date} using table '{full_table_name}'.")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    def _execute_trade(self, symbol, timestamp, current_data, action, slippage, commission, quantity=None):
        """
        Simulates the execution of a trade.
        """
        price = current_data['close']
        if action == 'BUY':
            execution_price = price + (price * slippage)
        elif action == 'SELL':
            execution_price = price - (price * slippage)
        else:
            return None

        if quantity is None:
            # Default quantity logic (you might want to customize this based on your strategy)
            quantity = 1

        trade = {
            'symbol': symbol,
            'timestamp': timestamp,
            'action': action,
            'price': execution_price,
            'quantity': quantity,
            'commission': execution_price * quantity * commission,
            'profit': 0.0  # Initialize profit to 0
        }
        return trade

    def _analyze_performance(self):
        if not self.trades:
            return {}

        df = pd.DataFrame(self.trades)
        df['trade_value'] = df['price'] * df['quantity']
        df['profit'] = 0.0
        position = 0
        entry_price = 0

        for index, row in df.iterrows():
            if row['action'] == 'BUY' and position == 0:
                position = row['quantity']
                entry_price = row['price']
            elif row['action'] == 'SELL' and position > 0 and row['symbol'] == df.iloc[0]['symbol']:
                profit_per_unit = row['price'] - entry_price
                df.loc[index, 'profit'] = profit_per_unit * position - row['commission']
                position = 0
                entry_price = 0
            elif row['action'] == 'SELL' and position < 0 and row['symbol'] == df.iloc[0]['symbol']:
                profit_per_unit = entry_price - row['price']
                df.loc[index, 'profit'] = profit_per_unit * abs(position) - row['commission']
                position = 0
                entry_price = 0
            elif row['action'] == 'BUY' and position < 0 and row['symbol'] == df.iloc[0]['symbol']:
                profit_per_unit = entry_price - row['price']
                df.loc[index, 'profit'] = profit_per_unit * abs(position) - row['commission']
                position = 0
                entry_price = 0
            elif row['action'] == 'BUY' and position == 0:
                position = row['quantity']
                entry_price = row['price']

        total_profit = df['profit'].sum()
        num_trades = len(df)
        winning_trades = len(df[df['profit'] > 0])
        losing_trades = len(df[df['profit'] < 0])

        win_rate = (winning_trades / num_trades) * 100 if num_trades > 0 else 0
        avg_profit = df['profit'].mean()
        max_profit = df['profit'].max()
        max_loss = df['profit'].min()

        performance = {
            'total_profit': total_profit,
            'num_trades': num_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_profit_per_trade': avg_profit,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'final_capital': self.current_capital
        }
        return performance

    async def run(self, symbol, start_date, end_date, timeframe='1m', slippage=0.0, commission=0.0,
                  custom_table_name=None):
        """
        Fetches historical data and runs the strategy to generate trades for a single symbol.
        """
        historical_data = await self._fetch_historical_data(symbol, start_date, end_date, timeframe, custom_table_name)
        # print(historical_data.head())
        # print(historical_data.shape)
        # print(historical_data.columns)
        # print(timeframe)

        if historical_data.empty:
            return [], {}

        self.strategy_instance = self.strategy_class(historical_data.copy(), self.strategy_params)
        if hasattr(self.strategy_instance, 'initialize'):
            self.strategy_instance.initialize(self.initial_capital)

        self.trades = []
        self.current_capital = self.initial_capital
        self.positions = {}

        # Apply the strategy to generate signals
        self.strategy_instance.apply_strategy()
        signals = self.strategy_instance.signals

        # Generate trades from signals
        for index, row in signals.iterrows():
            signal = row['signal']
            current_data = historical_data.loc[index]
            if signal:
                trade = self._execute_trade(symbol, index, current_data, 'BUY' if signal == 1 else 'SELL', slippage,
                                            commission)
                if trade:
                    self.trades.append(trade)
                    # Update capital and positions based on the trade (Simplified for basic backtesting)
                    if trade['action'] == 'BUY':
                        self.positions[symbol] = self.positions.get(symbol, 0) + trade['quantity']
                        self.current_capital -= (trade['price'] * trade['quantity']) + trade['commission']
                    elif trade['action'] == 'SELL':
                        self.positions[symbol] = self.positions.get(symbol, 0) - trade['quantity']
                        self.current_capital += (trade['price'] * trade['quantity']) - trade['commission']
                    logger.info(f"Executed trade: {trade}")

        performance = self._analyze_performance()
        return self.trades, performance
