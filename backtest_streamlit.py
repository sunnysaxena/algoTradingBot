import streamlit as st
import pandas as pd
import json
import plotly.graph_objs as go
import plotly.express as px  # For simplified graph creation

# Load Backtest Results from JSON
def load_backtest_results(filepath="backtest_results.json"):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

backtest_results = load_backtest_results()

st.title("Backtesting Results Dashboard")

# Dropdowns
strategy_options = [r["strategy"] for r in backtest_results]
selected_strategy = st.selectbox("Select a Strategy", [""] + strategy_options)

if selected_strategy:
    symbol_options = list(set([r["symbol"] for r in backtest_results if r["strategy"] == selected_strategy]))
    selected_symbol = st.selectbox("Select a Symbol", [""] + symbol_options)

    if selected_symbol:
        timeframe_options = list(set([r["timeframe"] for r in backtest_results if r["strategy"] == selected_strategy and r["symbol"] == selected_symbol]))
        selected_timeframe = st.selectbox("Select a Timeframe", [""] + timeframe_options)

        if selected_timeframe:
            result = next((r for r in backtest_results if r["strategy"] == selected_strategy and r["symbol"] == selected_symbol and r["timeframe"] == selected_timeframe), None)

            if result and result["performance"]:
                performance = result["performance"]

                # Performance Metrics Display
                st.subheader("Performance Metrics")
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Metric**")
                    for key in performance:
                        st.write(key.replace("_", " ").title())  # Display metric names nicely
                with col2:
                    st.write("**Value**")
                    for value in performance.values():
                        st.write(str(value))

            if result and result["trades"]:
                st.subheader("Trades Table")
                df = pd.DataFrame(result["trades"])
                st.dataframe(df)

                # Cumulative Profit Graph
                st.subheader("Cumulative Profit")
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.sort_values(by="timestamp")
                df["cumulative_profit"] = df["profit"].cumsum()
                fig_cumulative_profit = px.line(df, x="timestamp", y="cumulative_profit", title="Cumulative Profit")
                st.plotly_chart(fig_cumulative_profit)

                # Drawdown Graph
                st.subheader("Drawdown")
                df["peak"] = df["cumulative_profit"].cummax()
                df["drawdown"] = df["cumulative_profit"] - df["peak"]
                fig_drawdown = px.line(df, x="timestamp", y="drawdown", title="Drawdown")
                st.plotly_chart(fig_drawdown)

            else:
                st.write("No trades found.")
        else:
            st.write("Please select a timeframe.")
    else:
        st.write("Please select a symbol.")
else:
    st.write("Please select a strategy.")