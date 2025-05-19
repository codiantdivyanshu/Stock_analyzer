import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Stock Analyzer", layout="centered")
st.title("📊 Stock Analyzer App (Supports NSE, BSE, NASDAQ)")

# UI Inputs
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

# Analyze Button
if st.button("Analyze Stock", key="analyze_btn"):
    if not symbol:
        st.warning("⚠️ Please enter a stock symbol.")
    else:
        try:
            st.info(f"📉 Fetching data for: {full_symbol}")
            stock = yf.Ticker(full_symbol)
            hist = stock.history(period=period_option)

            if hist.empty:
                st.warning(f"No data found for {full_symbol}. Please check the symbol and exchange.")
            else:
                st.success(f"📈 Showing historical data for: {full_symbol}")
                st.line_chart(hist["Close"])
                st.write("🕒 Recent Price Data")
                st.dataframe(hist.tail())

                info = stock.info
                st.write("ℹ️ Company Info")
                st.write(info.get("longBusinessSummary", "No summary available."))

        except Exception as e:
            st.error(f"❌ Error fetching data: {e}")
