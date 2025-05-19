import streamlit as st
import yfinance as yf
from nsepython import nse_eq

st.set_page_config(page_title="Stock Analyzer", layout="centered")
st.title("📊 Stock Analyzer App (Supports NSE, BSE, NASDAQ)")

exchange = st.selectbox("Select Stock Exchange", ["NSE", "BSE", "NASDAQ", "NYSE"])
symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE, SBIN, AAPL)").upper()
period_option = st.selectbox("Select time period to analyze:", ["1y", "2y", "5y", "10y", "max"])

# Adjust full symbol for yfinance
if exchange == "NSE":
    full_symbol = symbol + ".NS"
elif exchange == "BSE":
    full_symbol = symbol + ".BO"
else:
    full_symbol = symbol

if st.button("Analyze Stock", key="analyze_btn"):
    if not symbol:
        st.warning("⚠️ Please enter a stock symbol.")
    else:
        try:
            # Try getting real-time data (NSE only)
            if exchange == "NSE":
                st.info(f"📡 Fetching real-time data for NSE symbol: {symbol}")
                try:
                    data = nse_eq(symbol)
                    if not data or not isinstance(data, dict):
                        raise ValueError("No valid response from nse_eq")

                    company_name = data.get("info", {}).get("companyName", "N/A")
                    price_info = data.get("priceInfo", {})
                    last_price = price_info.get("lastPrice", "N/A")
                    day_high = price_info.get("intraDayHighLow", {}).get("max", "N/A")
                    day_low = price_info.get("intraDayHighLow", {}).get("min", "N/A")
                    prev_close = price_info.get("previousClose", "N/A")

                    st.success(f"📈 Current data for {symbol} on NSE")
                    st.write(f"💼 Company Name: {company_name}")
                    st.write(f"📊 Current Price: ₹{last_price}")
                    st.write(f"📅 As of: {price_info.get('lastUpdateTime', 'N/A')}")

                    st.write("📋 Price Snapshot")
                    st.table({
                        "Open": prev_close,
                        "High": day_high,
                        "Low": day_low,
                        "Close": last_price,
                        "Previous Close": prev_close
                    })
                except Exception as real_time_err:
                    st.warning(f"⚠️ Real-time NSE data unavailable: {real_time_err}")

            # Always show historical chart with yfinance
            st.info("📉 Fetching historical chart data...")
            stock = yf.Ticker(full_symbol)
            hist = stock.history(period=period_option)

            if hist.empty:
                st.warning("No historical chart data found.")
            else:
                st.line_chart(hist["Close"])
                st.dataframe(hist.tail())

                info = stock.info
                if "longBusinessSummary" in info:
                    st.write("ℹ️ Company Info")
                    st.write(info.get("longBusinessSummary", "No summary available."))

        except Exception as e:
            st.error(f"❌ Error fetching data: {e}")
