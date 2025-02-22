import pandas as pd
import pandas_ta as ta


class EMARsiCrossover:
    """
    Implements an EMA and RSI crossover strategy to generate buy/sell signals.
    """

    def __init__(self, short_ema_period=9, long_ema_period=21, rsi_period=14, rsi_overbought=70, rsi_oversold=30):
        """
        Initialize the strategy with EMA and RSI parameters.

        :param short_ema_period: Period for short-term EMA.
        :param long_ema_period: Period for long-term EMA.
        :param rsi_period: Period for RSI calculation.
        :param rsi_overbought: Overbought threshold for RSI.
        :param rsi_oversold: Oversold threshold for RSI.
        """
        self.short_ema_period = short_ema_period
        self.long_ema_period = long_ema_period
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def compute_indicators(self, data):
        """
        Compute EMA and RSI indicators using pandas_ta.

        :param data: DataFrame containing historical price data with 'close' column.
        :return: DataFrame with EMA and RSI values added.
        """
        data[f'Short_EMA'] = ta.ema(data['close'], length=self.short_ema_period)
        data[f'Long_EMA'] = ta.ema(data['close'], length=self.long_ema_period)
        data['RSI'] = ta.rsi(data['close'], length=self.rsi_period)
        return data

    def generate_signals(self, data):
        """
        Generate buy/sell signals based on EMA and RSI crossover strategy.

        :param data: DataFrame with computed indicators.
        :return: List of trading signals.
        """
        signals = []
        for i in range(1, len(data)):
            if data['Short_EMA'][i] > data['Long_EMA'][i] and data['RSI'][i] < self.rsi_overbought:
                signals.append('BUY')
            elif data['Short_EMA'][i] < data['Long_EMA'][i] and data['RSI'][i] > self.rsi_oversold:
                signals.append('SELL')
            else:
                signals.append('HOLD')
        return signals
