import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import json
import plotly.graph_objs as go

# Load Backtest Results from JSON
def load_backtest_results(filepath="backtest_results.json"):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

backtest_results = load_backtest_results()

app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Backtesting Results Dashboard"),

    dcc.Dropdown(
        id="strategy-dropdown",
        options=[{"label": r["strategy"], "value": r["strategy"]} for r in backtest_results],
        multi=False,
        placeholder="Select a Strategy",
    ),

    dcc.Dropdown(
        id="symbol-dropdown",
        options=[],
        multi=False,
        placeholder="Select a Symbol",
    ),

    dcc.Dropdown(
        id="timeframe-dropdown",
        options=[],
        multi=False,
        placeholder="Select a Timeframe",
    ),

    html.Div(id="performance-output"),
    html.Div(id="trades-table-output"),
    dcc.Graph(id="cumulative-profit-graph"),
    dcc.Graph(id="drawdown-graph"),
])

# Callbacks
@app.callback(
    Output("symbol-dropdown", "options"),
    Input("strategy-dropdown", "value"),
)
def update_symbol_dropdown(selected_strategy):
    if selected_strategy:
        symbols = list(set([r["symbol"] for r in backtest_results if r["strategy"] == selected_strategy]))
        return [{"label": s, "value": s} for s in symbols]
    else:
        return []

@app.callback(
    Output("timeframe-dropdown", "options"),
    Input("strategy-dropdown", "value"),
    Input("symbol-dropdown", "value"),
)
def update_timeframe_dropdown(selected_strategy, selected_symbol):
    if selected_strategy and selected_symbol:
        timeframes = list(set([r["timeframe"] for r in backtest_results if r["strategy"] == selected_strategy and r["symbol"] == selected_symbol]))
        return [{"label": t, "value": t} for t in timeframes]
    else:
        return []

@app.callback(
    Output("performance-output", "children"),
    Input("strategy-dropdown", "value"),
    Input("symbol-dropdown", "value"),
    Input("timeframe-dropdown", "value"),
)
def update_performance_output(selected_strategy, selected_symbol, selected_timeframe):
    if selected_strategy and selected_symbol and selected_timeframe:
        result = next((r for r in backtest_results if r["strategy"] == selected_strategy and r["symbol"] == selected_symbol and r["timeframe"] == selected_timeframe), None)
        if result and result["performance"]:
            performance = result["performance"]
            return html.Div([
                html.Div([html.Strong("Metric"), html.Strong("Value")], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Total Trades"), html.Span(str(performance.get("total_trades", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Winning Trades"), html.Span(str(performance.get("winning_trades", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Losing Trades"), html.Span(str(performance.get("losing_trades", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Win Rate"), html.Span(str(performance.get("win_rate", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Total Profit"), html.Span(str(performance.get("total_profit", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Average Profit"), html.Span(str(performance.get("average_profit", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Final Cumulative Profit"), html.Span(str(performance.get("final_cumulative_profit", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Max Drawdown"), html.Span(str(performance.get("max_drawdown", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Average Loss"), html.Span(str(performance.get("average_loss", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Std Dev Returns"), html.Span(str(performance.get("std_dev_returns", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Sharpe Ratio"), html.Span(str(performance.get("sharpe_ratio", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Max Profit"), html.Span(str(performance.get("max_profit", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Max Loss"), html.Span(str(performance.get("max_loss", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Profit Factor"), html.Span(str(performance.get("profit_factor", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Average Holding Time"), html.Span(str(performance.get("average_holding_time", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Average Trade Duration"), html.Span(str(performance.get("average_trade_duration", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Trades Per Day"), html.Span(str(performance.get("trades_per_day", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Consistency Ratio"), html.Span(str(performance.get("consistency_ratio", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Profit Loss Ratio"), html.Span(str(performance.get("profit_loss_ratio", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Skewness"), html.Span(str(performance.get("skewness", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
                html.Div([html.Span("Kurtosis"), html.Span(str(performance.get("kurtosis", "N/A")))], style={"display": "grid", "grid-template-columns": "1fr 1fr"}),
            ])
        else:
            return "Performance data not found."
    else:
        return ""

@app.callback(
    Output("trades-table-output", "children"),
    Input("strategy-dropdown", "value"),
    Input("symbol-dropdown", "value"),
    Input("timeframe-dropdown", "value"),
)
def update_trades_table_output(selected_strategy, selected_symbol, selected_timeframe):
    if selected_strategy and selected_symbol and selected_timeframe:
        result = next((r for r in backtest_results if r["strategy"] == selected_strategy and r["symbol"] == selected_symbol and r["timeframe"] == selected_timeframe), None)
        if result and result["trades"]:
            df = pd.DataFrame(result["trades"])
            return dash_table.DataTable(
                data=df.to_dict("records"),
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=10,
            )
        else:
            return "No trades found."
    else:
        return ""

@app.callback(
    [Output("cumulative-profit-graph", "figure"), Output("drawdown-graph", "figure")],
    Input("strategy-dropdown", "value"),
    Input("symbol-dropdown", "value"),
    Input("timeframe-dropdown", "value"),
)
def update_graphs(selected_strategy, selected_symbol, selected_timeframe):
    if selected_strategy and selected_symbol and selected_timeframe:
        result = next((r for r in backtest_results if r["strategy"] == selected_strategy and r["symbol"] == selected_symbol and r["timeframe"] == selected_timeframe), None)
        if result and result["trades"]:
            df = pd.DataFrame(result["trades"])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values(by="timestamp")
            df["cumulative_profit"] = df["profit"].cumsum()

            # Cumulative Profit Graph
            cumulative_profit_fig = go.Figure(
                data=[go.Scatter(x=df["timestamp"], y=df["cumulative_profit"], mode="lines")],
                layout=go.Layout(title="Cumulative Profit", xaxis_title="Time", yaxis_title="Profit"),
            )

            # Drawdown Graph (Simple Example)
            df["peak"] = df["cumulative_profit"].cummax()
            df["drawdown"] = df["cumulative_profit"] - df["peak"]

            drawdown_fig = go.Figure(
                data=[go.Scatter(x=df["timestamp"], y=df["drawdown"], mode="lines")],
                layout=go.Layout(title="Drawdown", xaxis_title="Time", yaxis_title="Drawdown"),
            )

            return cumulative_profit_fig, drawdown_fig
        else:
            return go.Figure(), go.Figure()
    else:
        return go.Figure(), go.Figure()

if __name__ == "__main__":
    app.run(debug=True)