import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Multi-Stock Analyzer", layout="wide")

st.title("📊 Multi-Stock Analyzer and Comparison Tool")
st.markdown("Compare historical stock performance, returns, and risk metrics across multiple stocks.")

# ----- Limit max stocks and date range -----
MAX_STOCKS = 5
MAX_DAYS = 365 * 2  # max 2 years

# ----- User Inputs (must come before fetch_data call) -----
st.subheader("Select or Enter Stock Symbols")

default_stocks = ['AAPL', 'GOOG', 'MSFT', 'TSLA', 'INFY.BO', 'RELIANCE.BO']
selected_stocks = st.multiselect("Choose from list or enter below:", default_stocks)

custom_input = st.text_input("Or enter comma-separated symbols (e.g., TCS.NS, HDFCBANK.NS)")

if custom_input:
    selected_stocks += [s.strip().upper() for s in custom_input.split(',') if s.strip()]
    selected_stocks = list(set(selected_stocks))

# Limit number of stocks
if len(selected_stocks) > MAX_STOCKS:
    st.warning(f"Limiting selection to first {MAX_STOCKS} stocks to improve performance.")
    selected_stocks = selected_stocks[:MAX_STOCKS]

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime(2020, 1, 1))
with col2:
    end_date = st.date_input("End Date", datetime.today())

# Limit date range
if (end_date - start_date).days > MAX_DAYS:
    st.warning(f"Date range limited to {MAX_DAYS} days for performance.")
    start_date = end_date - timedelta(days=MAX_DAYS)

# ------------------ Cache data fetching ------------------

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_data(tickers, start, end):
    stock_data = {}
    for ticker in tickers:
        try:
            df = yf.Ticker(ticker).history(start=start, end=end)
            if df.empty or 'Close' not in df.columns:
                st.warning(f"No data returned for {ticker}.")
                continue
            if 'Adj Close' not in df.columns:
                df['Adj Close'] = df['Close']
            df['Return'] = df['Adj Close'].pct_change()
            stock_data[ticker] = df.dropna()
        except Exception as e:
            st.warning(f"Could not fetch data for {ticker}: {e}")
            continue
    return stock_data

stock_data = fetch_data(selected_stocks, start_date, end_date)

if not stock_data:
    st.error("No valid stock data was fetched. Please check your stock selections and date range.")
    st.stop()

# ------------------- Forecasting Options -------------------
st.subheader("📉 Forecasting Options")

forecast_ticker = st.selectbox("Select a stock to forecast", selected_stocks)
forecast_model = st.radio("Choose Forecasting Model", ["ARIMA", "Prophet"])
forecast_period = st.slider("Forecast Horizon (days)", min_value=7, max_value=90, value=30)

# -------- Cache model loading and forecast results --------

# Cache ARIMA model loading and forecasting
@st.cache_data(ttl=3600)
def run_arima_forecast(series, periods):
    from pmdarima import auto_arima
    model = auto_arima(series, seasonal=False, stepwise=True, suppress_warnings=True)
    forecast = model.predict(n_periods=periods)
    return forecast

# Cache Prophet model loading and forecasting
@st.cache_data(ttl=3600)
def run_prophet_forecast(df, periods):
    from prophet import Prophet
    prophet_df = df.reset_index()[['Date', 'Adj Close']].rename(columns={'Date': 'ds', 'Adj Close': 'y'})
    model = Prophet()
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return prophet_df, forecast

if forecast_ticker in stock_data:
    df = stock_data[forecast_ticker].copy()

    st.subheader(f"📉 Forecast for {forecast_ticker} using {forecast_model}")

    if forecast_model == "ARIMA":
        series = df['Adj Close']
        future = run_arima_forecast(series, forecast_period)
        future_dates = pd.date_range(df.index[-1] + timedelta(days=1), periods=forecast_period)
        forecast_df = pd.DataFrame({'Date': future_dates, 'Forecast': future})

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=series, name="Historical"))
        fig.add_trace(go.Scatter(x=forecast_df['Date'], y=forecast_df['Forecast'], name="Forecast"))
        st.plotly_chart(fig, use_container_width=True)

    elif forecast_model == "Prophet":
        prophet_df, forecast = run_prophet_forecast(df, forecast_period)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prophet_df['ds'], y=prophet_df['y'], name="Historical"))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], name="Forecast"))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], name="Upper", line=dict(dash='dot')))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], name="Lower", line=dict(dash='dot')))
        st.plotly_chart(fig, use_container_width=True)

# ------------------- Chart -------------------

st.subheader("📈 Price Trend Comparison")
fig = go.Figure()
for ticker in stock_data:
    fig.add_trace(go.Scatter(x=stock_data[ticker].index,
                             y=stock_data[ticker]['Adj Close'],
                             name=ticker))
fig.update_layout(title="Adjusted Close Prices",
                  xaxis_title="Date",
                  yaxis_title="Price",
                  height=500)
st.plotly_chart(fig, use_container_width=True)

# ------------------- Performance -------------------

st.subheader("📊 Performance Metrics")

stats = []
for ticker in stock_data:
    df = stock_data[ticker]
    returns = df['Return'].dropna()
    total_return = (df['Adj Close'].iloc[-1] / df['Adj Close'].iloc[0]) - 1
    volatility = returns.std()
    stats.append({
        "Stock": ticker,
        "Total Return (%)": round(total_return * 100, 2),
        "Avg Daily Return (%)": round(returns.mean() * 100, 2),
        "Volatility (Std Dev)": round(volatility, 4)
    })

stats_df = pd.DataFrame(stats).sort_values(by="Total Return (%)", ascending=False)
st.dataframe(stats_df, use_container_width=True)

# ------------------- Correlation -------------------

st.subheader("📌 Return Correlation Matrix")
returns_df = pd.DataFrame({ticker: stock_data[ticker]['Return'] for ticker in stock_data}).dropna()
correlation = returns_df.corr()
st.write(correlation.style.background_gradient(cmap='coolwarm'))

# ------------------- Export -------------------

st.subheader("⬇️ Export Performance Data")
csv = stats_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Metrics as CSV", csv, "stock_metrics.csv", "text/csv")

# ------------------- AI Summary -------------------

st.subheader("🧠 AI Summary (Experimental)")
try:
    top = stats_df.iloc[0]
    bottom = stats_df.iloc[-1]
    st.markdown(f"**Best Performer:** {top['Stock']} with {top['Total Return (%)']}% return")
    st.markdown(f"**Worst Performer:** {bottom['Stock']} with {bottom['Total Return (%)']}% return")
    avg_return = stats_df['Total Return (%)'].mean()
    st.markdown(f"**Average Total Return across selected stocks:** {round(avg_return, 2)}%")
except Exception as e:
    st.info(f"Summary unavailable: {e}")
