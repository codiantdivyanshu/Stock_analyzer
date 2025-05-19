import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("📈 Stock Analyzer App")

symbol = st.text_input("Enter stock symbol (e.g., AAPL, TSLA, GOOGL)", "AAPL").upper()

stock = yf.Ticker(symbol)
df = stock.history(period="1y")

if st.checkbox("Show raw data"):
    st.subheader(f"{symbol} Raw Data (Last 1 Year)")
    st.write(df)

st.subheader(f"{symbol} Closing Price")
st.line_chart(df['Close'])

df['MA50'] = df['Close'].rolling(window=50).mean()
df['MA200'] = df['Close'].rolling(window=200).mean()

st.subheader("Moving Averages")
st.line_chart(df[['Close', 'MA50', 'MA200']])

try:
    st.subheader("Company Summary")
    st.write(stock.info['longBusinessSummary'])
except:
    st.warning("Company summary not available.")

if st.checkbox("Show Additional Stats"):
    st.markdown(f"**Market Cap**: {stock.info.get('marketCap', 'N/A')}")
    st.markdown(f"**52 Week High**: {stock.info.get('fiftyTwoWeekHigh', 'N/A')}")
    st.markdown(f"**PE Ratio**: {stock.info.get('trailingPE', 'N/A')}")

