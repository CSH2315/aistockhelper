import requests
import os
from dotenv import load_dotenv
from fastapi import FastAPI

app = FastAPI()

load_dotenv()
YAHOO_API_KEY = os.environ.get('YAHOO_API_KEY')
YAHOO_API_HOST = "yahoo-finance15.p.rapidapi.com"

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI API"}

# 해외주식: Yahoo Finance API 사용
@app.get("/news/global/{symbol}")
def get_global_stock_news(symbol: str):
    url = f"https://{YAHOO_API_HOST}/api/yahoo/ne/news/{symbol}"
    headers = {
        'x-rapidapi-key': YAHOO_API_KEY,
        'x-rapidapi-host': YAHOO_API_HOST
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        news_data = response.json()
        return news_data
    return {"error: Failed to fetch"}