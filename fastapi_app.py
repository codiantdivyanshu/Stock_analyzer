from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional, Dict, Any
import yfinance as yf
import pandas as pd
from datetime import date

app = FastAPI(title="Stock Analyzer API")


def fetch_stock_data(tickers: List[str], start_date: date, end_date: date) -> Dict[str, Any]:
    """
    Fetch historical stock data for multiple tickers between given dates.

    Args:
        tickers (List[str]): List of stock ticker symbols.
        start_date (date): Start date for historical data.
        end_date (date): End date for historical data.

    Returns:
        Dict[str, Any]: Dictionary with tickers as keys and their data as list of dicts.
    """
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start_date, end=end_date)
            if df.empty:
                continue
            data[ticker] = df.reset_index().to_dict(orient='records')
        except Exception:
            # Log or handle errors if needed, skipping ticker on failure here
            continue
    return data


@app.get("/", summary="Root endpoint")
async def root():
    """Basic root endpoint to check API status."""
    return {"message": "Welcome to Stock Analyzer API"}


@app.get("/stock", summary="Get latest 1 month stock data for a single ticker")
async def get_stock_data(
    ticker: str = Query(..., description="Stock ticker symbol, e.g. AAPL")
):
    """
    Fetch the latest 1 month stock data for a single ticker symbol.

    Args:
        ticker (str): Stock ticker symbol.

    Returns:
        dict: Dictionary containing ticker symbol and historical data list.
    """
    try:
        df = yf.Ticker(ticker).history(period="1mo")
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for ticker '{ticker}'")

        data = df.reset_index().to_dict(orient="records")
        return {"ticker": ticker, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@app.get("/stocks", summary="Get historical stock data for multiple tickers")
async def get_stocks(
    tickers: List[str] = Query(..., description="List of stock ticker symbols, e.g. ['AAPL', 'MSFT']"),
    start_date: Optional[date] = Query(date(2020, 1, 1), description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(date.today(), description="End date (YYYY-MM-DD)"),
):
    """
    Fetch historical stock data for multiple tickers over a date range.

    Args:
        tickers (List[str]): List of stock ticker symbols.
        start_date (date, optional): Start date for data. Defaults to 2020-01-01.
        end_date (date, optional): End date for data. Defaults to today.

    Returns:
        dict: Dictionary with tickers as keys and their data as lists.
    """
    stock_data = fetch_stock_data(tickers, start_date, end_date)
    if not stock_data:
        raise HTTPException(status_code=404, detail="No data found for given tickers and date range.")
    return stock_data
