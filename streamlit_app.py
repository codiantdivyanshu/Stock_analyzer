import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from datetime import datetime

st.set_page_config(page_title="Multi-Stock Analyzer", layout="wide")

st.title("📊 Multi-Stock Analyzer and Comparison Tool")
st.markdown("Compare historical stock performance, returns, and risk metrics across multiple stocks.")

# Sample tickers (US and India NSE)
stock_list = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'INFY.NS', 'TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS', 'SBIN.NS']
selected_stocks = st.multiselect("Select Stocks to Compare", stock_list, default=['AAPL', 'MSFT', 'RELIANCE.NS'])

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime(2023, 1, 1))
with col2:
    end_date = st.date_input("End Date", datetime.today())


@st.cache_data
def fetch_data(tickers, start, end):
    stock_data = {}

    for ticker in tickers:
        try:
            df = yf.Ticker(ticker).history(start=start, end=end)
            if df.empty or 'Close' not in df.columns:
                st.warning(f"No data returned for {ticker}.")
                continue

            # Adjusted Close fallback if missing
            if 'Adj Close' not in df.columns:
                df['Adj Close'] = df['Close']

            df['Return'] = df['Adj Close'].pct_change()
            stock_data[ticker] = df.dropna()
        except Exception as e:
            st.warning(f"Could not fetch data for {ticker}: {e}")
            continue

    return stock_data

# ---------------- Use the Function ----------------

stock_data = fetch_data(selected_stocks, start_date, end_date)

stock_data = fetch_data(selected_stocks, start_date, end_date)

if not stock_data:
    st.error("No valid stock data was fetched. Please check your stock selections and date range.")
    st.stop()

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
st.dataframe(correlation.style.background_gradient(cmap='coolwarm'), use_container_width=True)

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
