import FastAPI, HTTPException, Query from fastapi 
import List, Optional, Dict, Any from typing 
import yfinance as yf
import date from datetime 
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to Stock Analyzer API"}


def fetch_stock_data(tickers: List[str], start_date: date, end_date: date) -> Dict[str, Any]:
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start_date, end=end_date)
            if df.empty:
                continue
            data[ticker] = df.reset_index().to_dict(orient='records')
        except Exception:
            continue
    return data

@app.get("/", summary="Root endpoint")
async def root():
    return {"message": "Welcome to Stock Analyzer API"}

@app.get("/stock", summary="Get latest 1 month stock data for a single ticker")
async def get_stock_data(ticker: str = Query(..., description="Stock ticker symbol, e.g. AAPL")):
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
    tickers: List[str] = Query(..., description="List of stock ticker symbols"),
    start_date: Optional[date] = Query(date(2020, 1, 1), description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(date.today(), description="End date (YYYY-MM-DD)"),
):
    stock_data = fetch_stock_data(tickers, start_date, end_date)
    if not stock_data:
        raise HTTPException(status_code=404, detail="No data found for given tickers and date range.")
    return stock_data
