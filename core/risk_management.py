class RiskManagement:
    """
    Handles risk management for algorithmic trading strategies.
    Includes position sizing, stop-loss, and risk-reward calculations.
    """

    def __init__(self, config):
        """
        Initialize risk management settings.

        :param config: Dictionary containing risk parameters.
        """
        self.max_risk_per_trade = config.get("max_risk_per_trade", 0.02)  # Default 2% risk per trade
        self.account_balance = config.get("account_balance", 100000)  # Default account balance

    def calculate_position_size(self, entry_price, stop_loss_price):
        """
        Calculate position size based on risk per trade and stop-loss level.

        :param entry_price: Price at which the trade is entered.
        :param stop_loss_price: Price at which the trade will be exited to prevent further loss.
        :return: Number of shares/contracts to trade.
        """
        risk_amount = self.max_risk_per_trade * self.account_balance
        risk_per_share = abs(entry_price - stop_loss_price)
        if risk_per_share == 0:
            return 0  # Avoid division by zero
        position_size = risk_amount / risk_per_share
        return int(position_size)

    def set_stop_loss(self, entry_price, risk_reward_ratio=2):
        """
        Determine stop-loss and target price based on risk-reward ratio.

        :param entry_price: Price at which the trade is entered.
        :param risk_reward_ratio: Ratio of reward to risk (default is 2:1).
        :return: Tuple of (stop_loss_price, target_price).
        """
        stop_loss_price = entry_price * (1 - self.max_risk_per_trade)
        target_price = entry_price + (entry_price - stop_loss_price) * risk_reward_ratio
        return stop_loss_price, target_price
