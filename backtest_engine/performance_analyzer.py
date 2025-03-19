import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """
    Analyzes the performance of a trading strategy based on executed trades.
    """
    def __init__(self, trades):
        """
        Initializes the PerformanceAnalyzer.

        Args:
            trades (list): A list of trade dictionaries.
        """
        self.trades_df = pd.DataFrame(trades)
        if not self.trades_df.empty:
            self.trades_df['cumulative_profit'] = self.trades_df['profit'].cumsum()
            self.trades_df['win'] = np.where(self.trades_df['profit'] > 0, 1, 0)
            self.trades_df['loss'] = np.where(self.trades_df['profit'] < 0, 1, 0)
            if 'entry_time' in self.trades_df.columns and 'exit_time' in self.trades_df.columns:
                self.trades_df['holding_period'] = (pd.to_datetime(self.trades_df['exit_time']) - pd.to_datetime(self.trades_df['entry_time']))

    def analyze(self):
        """
        Performs the performance analysis and returns a dictionary of metrics.
        """
        if self.trades_df.empty:
            return {"error": "No trades to analyze."}

        # 1. Performance Metrics
        total_trades = len(self.trades_df)
        winning_trades = self.trades_df['win'].sum()
        losing_trades = self.trades_df['loss'].sum()
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        total_profit = self.trades_df['profit'].sum()
        average_profit = self.trades_df['profit'].mean()
        cumulative_returns = self.trades_df['profit'].cumsum()
        final_cumulative_profit = self.trades_df['cumulative_profit'].iloc[-1] if not self.trades_df.empty else 0

        # 2. Risk Metrics
        max_drawdown = self._calculate_max_drawdown(cumulative_returns)
        average_loss = self.trades_df[self.trades_df['profit'] < 0]['profit'].mean()
        std_dev_returns = self.trades_df['profit'].std()
        sharpe_ratio = (average_profit / std_dev_returns) if std_dev_returns != 0 else np.inf #Assuming risk free rate is 0

        # 3. Trade-Specific Metrics
        max_profit = self.trades_df['profit'].max()
        max_loss = self.trades_df['profit'].min()
        profit_factor = -average_profit / average_loss if average_loss != 0 else np.inf
        average_holding_time = self.trades_df['holding_period'].mean() if 'holding_period' in self.trades_df.columns else None

        # 4. Efficiency Metrics
        average_trade_duration = self.trades_df['holding_period'].mean() if 'holding_period' in self.trades_df.columns else None
        trades_per_day = self._calculate_trades_per_day()

        # 5. Stability and Consistency Metrics
        consistency_ratio = (winning_trades / losing_trades) if losing_trades != 0 else np.inf
        profit_loss_ratio = abs(average_profit / average_loss) if average_loss != 0 else np.inf

        # 6. Statistical Metrics
        skewness = self.trades_df['profit'].skew()
        kurtosis = self.trades_df['profit'].kurtosis()

        results = {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": f"{win_rate:.2f}%",
            "total_profit": f"{total_profit:.2f}",
            "average_profit": f"{average_profit:.2f}",
            "final_cumulative_profit": f"{final_cumulative_profit:.2f}",
            "max_drawdown": f"{max_drawdown:.2f}",
            "average_loss": f"{average_loss:.2f}",
            "std_dev_returns": f"{std_dev_returns:.2f}",
            "sharpe_ratio": f"{sharpe_ratio:.2f}",
            "max_profit": f"{max_profit:.2f}",
            "max_loss": f"{max_loss:.2f}",
            "profit_factor": f"{profit_factor:.2f}",
            "average_holding_time": str(average_holding_time),
            "average_trade_duration": str(average_trade_duration),
            "trades_per_day": trades_per_day,
            "consistency_ratio": f"{consistency_ratio:.2f}",
            "profit_loss_ratio": f"{profit_loss_ratio:.2f}",
            "skewness": f"{skewness:.2f}",
            "kurtosis": f"{kurtosis:.2f}"
        }
        return results

    def _calculate_max_drawdown(self, cumulative_returns):
        """Calculates the maximum drawdown of the cumulative returns."""
        if cumulative_returns.empty:
            return 0.0
        peak = cumulative_returns.iloc[0]
        max_drawdown = 0
        for value in cumulative_returns:
            if value > peak:
                peak = value
            drawdown = (peak - value)
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        return max_drawdown

    def _calculate_trades_per_day(self):
        """Calculates the average number of trades per day."""
        if self.trades_df.empty or 'entry_time' not in self.trades_df.columns:
            return "N/A"
        try:
          first_trade_date = pd.to_datetime(self.trades_df['entry_time'].min()).date()
          last_trade_date = pd.to_datetime(self.trades_df['entry_time'].max()).date()
          num_days = (last_trade_date - first_trade_date).days + 1
          if num_days <= 0:
            return "N/A"
          return len(self.trades_df) / num_days
        except Exception as e:
            logger.error(f"Error calculating trades per day: {e}")
            return "N/A"