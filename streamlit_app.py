import streamlit as st
import yfinance as yf
from nsepython import nse_eq

ticker = yf.Ticker("RELIANCE.NS")
data = ticker.history(period="1y")

st.set_page_config(page_title="Stock Analyzer", layout="centered")
st.title("📊 Stock Analyzer App (Supports NSE, BSE, NASDAQ)")

exchange = st.selectbox("Select Stock Exchange", ["NSE", "BSE", "NASDAQ", "NYSE"])
symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE, SBIN, AAPL)").upper()
period_option = st.selectbox("Select time period to analyze:", ["1y", "2y", "5y", "10y", "max"])

# Adjust full symbol for yfinance
if exchange == "NSE":
    full_symbol = symbol + ".NS"  # yfinance NSE format
elif exchange == "BSE":
    full_symbol = symbol + ".BO"
else:
    full_symbol = symbol

if st.button("Analyze Stock", key="analyze_btn"):
    if not symbol:
        st.warning("⚠️ Please enter a stock symbol.")
    else:
        try:
            if exchange == "NSE":
                # Show real-time data using nsepython
                st.info(f"📡 Fetching real-time data for NSE symbol: {symbol}")
                data = nse_eq(symbol)

                if not data:
                    st.warning(f"No real-time data found for NSE symbol: {symbol}")
                else:
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

                # Show chart using yfinance (fallback for historical)
                st.info("📉 Fetching historical chart data from Yahoo Finance...")
                stock = yf.Ticker(symbol + ".NS")
                hist = stock.history(period=period_option)

                if hist.empty:
                    st.warning("No historical chart data found.")
                else:
                    st.line_chart(hist["Close"])
                    st.dataframe(hist.tail())

            else:
                # For non-NSE exchanges
                st.info(f"📉 Fetching data for: {full_symbol}")
                stock = yf.Ticker(full_symbol)
                data = stock.history(period=period_option)

                if data.empty:
                    st.warning(f"No data found for {full_symbol}. Please check the symbol and exchange.")
                else:
                    st.success(f"📈 Showing historical data for: {full_symbol}")
                    st.line_chart(data["Close"])
                    st.write("🕒 Recent Price Data")
                    st.dataframe(data.tail())

                    info = stock.info
                    st.write("ℹ️ Company Info")
                    st.write(info.get("longBusinessSummary", "No summary available."))

        except Exception as e:
            st.error(f"❌ Error fetching data: {e}")
