class SignalGenerator:
    """
    Generates trading signals based on technical indicators.
    Supports EMA, RSI, and crossover strategies.
    """

    def __init__(self, config):
        """
        Initialize signal generator with configuration.

        :param config: Dictionary containing indicator parameters.
        """
        self.ema_short_period = config.get("ema_short_period", 9)
        self.ema_long_period = config.get("ema_long_period", 21)
        self.rsi_period = config.get("rsi_period", 14)
        self.rsi_overbought = config.get("rsi_overbought", 70)
        self.rsi_oversold = config.get("rsi_oversold", 30)

    def calculate_ema(self, prices, period):
        """
        Calculate Exponential Moving Average (EMA).

        :param prices: List of historical prices.
        :param period: EMA period.
        :return: EMA value.
        """
        if len(prices) < period:
            return None
        ema = sum(prices[-period:]) / period  # Simplified calculation
        return ema

    def calculate_rsi(self, prices):
        """
        Calculate Relative Strength Index (RSI).

        :param prices: List of historical prices.
        :return: RSI value.
        """
        if len(prices) < self.rsi_period:
            return None
        gains = [max(0, prices[i] - prices[i - 1]) for i in range(1, len(prices))]
        losses = [max(0, prices[i - 1] - prices[i]) for i in range(1, len(prices))]
        avg_gain = sum(gains[-self.rsi_period:]) / self.rsi_period
        avg_loss = sum(losses[-self.rsi_period:]) / self.rsi_period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_signal(self, prices):
        """
        Generate buy/sell signals based on EMA crossover and RSI.

        :param prices: List of historical prices.
        :return: 'BUY', 'SELL', or 'HOLD'.
        """
        ema_short = self.calculate_ema(prices, self.ema_short_period)
        ema_long = self.calculate_ema(prices, self.ema_long_period)
        rsi = self.calculate_rsi(prices)

        if ema_short and ema_long and ema_short > ema_long and rsi and rsi < self.rsi_oversold:
            return "BUY"
        elif ema_short and ema_long and ema_short < ema_long and rsi and rsi > self.rsi_overbought:
            return "SELL"
        return "HOLD"
