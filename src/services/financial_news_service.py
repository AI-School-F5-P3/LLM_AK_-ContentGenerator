import requests
from typing import List, Dict
import yfinance as yf
from datetime import datetime, timedelta

class FinancialNewsService:
    def __init__(self, alpha_vantage_key: str):
        self.alpha_vantage_key = alpha_vantage_key
        
    def get_market_news(self) -> List[Dict]:
        # Get news from Alpha Vantage
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={self.alpha_vantage_key}"
        response = requests.get(url)
        data = response.json()
        
        # Get market data from Yahoo Finance
        indices = ["^GSPC", "^IXIC", "^DJI"]  # S&P 500, NASDAQ, Dow Jones
        market_data = {}
        
        for index in indices:
            ticker = yf.Ticker(index)
            hist = ticker.history(period="1d")
            market_data[index] = {
                "price": hist['Close'].iloc[-1],
                "change": hist['Close'].iloc[-1] - hist['Open'].iloc[-1]
            }
            
        return {
            "news": data.get("feed", [])[:5],  # Get top 5 news
            "market_data": market_data
        }