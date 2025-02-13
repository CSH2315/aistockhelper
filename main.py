import requests
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from bs4 import BeautifulSoup

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


# 국내주식: 네이버 웹 크롤링
@app.get("/news/korea/{symbol}")
def get_korean_stock_news(symbol: str):
    base_url = "https://search.naver.com/search.naver?where=news&query="
    search_url = base_url + symbol
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    news_list = []
    articles = soup.select("div.news_area")

    for article in articles[:20]:
        title = article.select_one("a.news_tit").text
        # pub_date = article.select_one(".info").text if article.select_one(".info") else "No Date information" # pubDate 가져오기
        link = article.select_one("a.news_tit").get("href")
        # guid = link # guid 가져오기
        description = article.select_one(".news_dsc").text if article.select_one(".news_dsc") else "No description"

        news_list.append({
            "description": description,
            # "guid": guid,
            "link": link,
            # "pubDate": pub_date,
            "title": title
        })

    return {"symbol": symbol, "news": news_list}