from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
import yfinance as yf
import pandas as pd
from datetime import date

app = FastAPI(title="Stock Analyzer API")

def fetch_stock_data(tickers: List[str], start_date: date, end_date: date):
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start_date, end=end_date)
            if df.empty:
                continue
            # Convert dataframe to dict for JSON serialization
            data[ticker] = df.reset_index().to_dict(orient='records')
        except Exception as e:
            # Skip ticker on error
            continue
    return data

@app.get("/stocks")
async def get_stocks(
    tickers: List[str] = Query(..., description="List of stock tickers"),
    start_date: Optional[date] = Query(date(2020,1,1), description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(date.today(), description="End date (YYYY-MM-DD)")
):
    stock_data = fetch_stock_data(tickers, start_date, end_date)
    if not stock_data:
        raise HTTPException(status_code=404, detail="No data found for given tickers and dates.")
    return stock_data
@app.get("/")
def root():
    return {"message": "Welcome to Stock Analyzer API"}

@app.get("/stock")
def get_stock_data(ticker: str = Query(..., description="Stock ticker symbol")):
    try:
        df = yf.Ticker(ticker).history(period="1mo")  # last 1 month data
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for ticker")

        # Prepare response data: convert DataFrame to dictionary for JSON
        data = df.reset_index().to_dict(orient="records")
        return {"ticker": ticker, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
