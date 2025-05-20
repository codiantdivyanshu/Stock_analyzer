from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from datetime import date
from stock_data import fetch_stock_data   # Import from separate module

app = FastAPI(title="Stock Analyzer API")

@app.get("/stocks")
async def get_stocks(
    tickers: List[str] = Query(..., description="List of stock tickers"),
    start_date: Optional[date] = Query(date(2020,1,1), description="Start date"),
    end_date: Optional[date] = Query(date.today(), description="End date")
):
    stock_data = fetch_stock_data(tickers, start_date, end_date)
    if not stock_data:
        raise HTTPException(status_code=404, detail="No data found for given tickers and dates.")
    return stock_data
