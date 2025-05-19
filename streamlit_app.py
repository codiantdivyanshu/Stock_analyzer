import streamlit as st
import yfinance as yf


from nsepython import nse_eq

st.set_page_config(page_title="Stock Analyzer", layout="centered")
st.title("📊 Stock Analyzer App (Supports NSE, BSE, NASDAQ)")


exchange = st.selectbox("Select Stock Exchange", ["NSE", "BSE", "NASDAQ", "NYSE"])
symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE, SBIN, AAPL)").upper()
period_option = st.selectbox("Select time period to analyze:", ["1y", "2y", "5y", "10y", "max"])

if exchange == "NSE":
    full_symbol = symbol 
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
                
                st.info(f"Fetching data for NSE symbol: {symbol}")
                data = nse_eq(symbol)

                if not data:
                    st.warning(f"No data found for NSE symbol: {symbol}")
                else:
                    st.success(f"📈 Current data for {symbol} on NSE")
                    st.write(f"💼 Company Name: {data.get('companyName', 'N/A')}")
                    st.write(f"📊 Current Price: ₹{data.get('lastPrice', 'N/A')}")
                    st.write(f"📅 As of: {data.get('lastUpdateTime', 'N/A')}")
                    st.json(data)

                    
                    st.write("📋 Price Snapshot")
                    st.table({
                        "Open": data.get("dayHigh", "N/A"),
                        "Low": data.get("dayLow", "N/A"),
                        "Close": data.get("lastPrice", "N/A"),
                        "Previous Close": data.get("previousClose", "N/A")
                    })

            else:
                
                st.info(f"Fetching data for: {full_symbol}")
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
