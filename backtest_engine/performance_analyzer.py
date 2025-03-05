import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class PerformanceAnalyzer:
    @staticmethod
    def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """Calculates Sharpe Ratio (Annualized)."""
        excess_returns = returns - risk_free_rate / 252  # Convert annual to daily rate
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        return round(sharpe_ratio, 2)

    @staticmethod
    def calculate_max_drawdown(cumulative_returns):
        """Calculates Maximum Drawdown."""
        peak = cumulative_returns.cummax()
        drawdown = (cumulative_returns - peak) / peak
        max_drawdown = drawdown.min() * 100  # Convert to percentage
        return round(max_drawdown, 2)

    @staticmethod
    def win_rate(trades):
        """Calculates the win rate of the strategy."""
        wins = trades[trades["PnL"] > 0].shape[0]
        total_trades = trades.shape[0]
        return round((wins / total_trades) * 100, 2) if total_trades > 0 else 0.0

    @staticmethod
    def monte_carlo_simulation(returns, simulations=1000, days=252):
        """Runs Monte Carlo simulations to model portfolio outcomes."""
        mean_return = np.mean(returns)
        std_dev = np.std(returns)

        simulated_paths = []
        for _ in range(simulations):
            daily_returns = np.random.normal(mean_return, std_dev, days)
            price_path = np.cumprod(1 + daily_returns)
            simulated_paths.append(price_path)

        simulated_paths = np.array(simulated_paths)
        plt.figure(figsize=(10, 5))
        plt.plot(simulated_paths.T, alpha=0.1, color="blue")
        plt.title("Monte Carlo Simulation of Portfolio Returns")
        plt.xlabel("Days")
        plt.ylabel("Portfolio Value Growth")
        plt.show()

    @staticmethod
    def generate_report(stats, trades):
        """Generates a detailed performance report."""
        print("\n📊 Backtest Performance Summary:")
        print(stats)

        returns = stats["_equity_curve"]["Equity"].pct_change().dropna()
        cumulative_returns = stats["_equity_curve"]["Equity"]

        sharpe_ratio = PerformanceAnalyzer.calculate_sharpe_ratio(returns)
        max_drawdown = PerformanceAnalyzer.calculate_max_drawdown(cumulative_returns)
        win_rate = PerformanceAnalyzer.win_rate(trades)

        print(f"\n✅ Final Portfolio Value: ${stats['Equity Final']:.2f}")
        print(f"📈 Max Drawdown: {max_drawdown:.2f}%")
        print(f"📊 Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"🔄 Win Rate: {win_rate:.2f}%")

        # Monte Carlo Simulation
        PerformanceAnalyzer.monte_carlo_simulation(returns)
