# Backtest Script


A `performance_analyzer.py` file in the **backtesting** module should analyze the performance of trading strategies based on historical data. It can compute key performance metrics like **CAGR, Sharpe ratio, max drawdown, win rate**, and more.








Here’s a Python script to backtest the EMA 9-21 & RSI Crossover Strategy using historical OHLC data. It includes trade execution logic, P&L calculation, and performance metrics.

**Features of the Backtest Script**

✅ Loads historical data from a CSV file or database

✅ Computes EMA (9 & 21) and RSI (14) using **pandas_ta**

✅ Implements entry & exit rules

✅ Tracks profit/loss per trade

✅ Plots equity curve & signals

<br>

**Enhancements for the EMA 9-21 & RSI Crossover Backtest**

To make the backtest more realistic and robust, here are some key enhancements:

✅ Include Stop-Loss & Take-Profit – Manage risk per trade

✅ Commission & Slippage Simulation – Account for real trading costs

✅ Multi-Timeframe Analysis – Validate signals with higher timeframes

✅ Database Integration – Fetch data from MySQL, InfluxDB, or TimescaleDB

✅ Trailing Stop-Loss – Lock in profits dynamically

✅ Position Sizing (Risk Management) – Allocate capital per trade

✅ Logging & Alerts – Send trade alerts via Telegram

<br>

# EMA (9 & 21) and RSI Crossover Strategy


### Advantages:
1. Combines Trend & Momentum Indicators

   * EMA (9 & 21) helps in identifying trends, while RSI provides momentum insights.
   * This combination improves accuracy in trend-following strategies.

2. Faster Response to Price Changes

   * EMA (Exponential Moving Average) reacts more quickly to price movements than SMA (Simple Moving Average), allowing early trend identification.
   * The 9-EMA crossing over the 21-EMA signals short-term trend shifts effectively.

3. Reduces False Signals with RSI

   * RSI (Relative Strength Index) prevents taking trades during overbought/oversold conditions, reducing false signals.
   * If a bullish EMA crossover aligns with RSI < 70, it strengthens the buy signal.

4. Works Well in Trending Markets

   * Performs well in strong trends where price continues in the direction of the crossover.
   * Can capture significant moves when trends sustain.

5. Simple and Widely Used

   * Easy to implement and backtest.
   * Many traders and institutions use similar strategies, adding to its effectiveness.


### Disadvantages:
1. Not Effective in Sideways Markets

   * During choppy or ranging markets, EMA crossovers can generate frequent false signals.
   * RSI may remain near the middle range (40-60), leading to indecision.

2. Lagging Nature of EMAs

   * Since EMAs are based on past prices, they lag behind actual price movements.
   * Signals may come late, especially during sudden price reversals.

3. RSI Can Stay Overbought/Oversold for Long Periods

   * In strong trends, RSI can remain above 70 (overbought) or below 30 (oversold) for an extended time, causing missed opportunities.

4. Prone to Whipsaws in Low Volatility Conditions

   * If volatility is low, price movements may frequently cross EMAs, leading to fake breakouts. 
   * Traders may enter and exit trades prematurely due to erratic movements.

5. Requires Additional Confirmation

   * To improve reliability, traders often combine this strategy with volume analysis, support/resistance levels, or other indicators.
   * Over-reliance on this strategy alone may lead to losses in uncertain market conditions.


### Best Practices for Using EMA 9-21 & RSI Crossover:

✅ Confirm EMA Crossovers with RSI – Look for RSI < 70 for buy signals and RSI > 30 for sell signals.

✅ Use in Trending Markets – `Avoid sideways conditions`.

✅ Combine with Support/Resistance – Enter trades near key levels.

✅ Set Stop-Loss and Risk Management – To prevent large drawdowns.

✅ Use Higher Timeframes `(e.g., 15m, 1h, daily)` – Reduces noise and false signals.

✅ Confirm with Volume or Other Indicators – Adds strength to the signal.

