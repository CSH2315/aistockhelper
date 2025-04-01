import os
import logging
import pytz
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI()
logger = logging.getLogger(__name__)


@app.get("/")
def root_test():
    return {"msg": "Hello"}


load_dotenv()
HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE-STOCK-API-KEY')
YAHOO_API_KEY = os.environ.get('YAHOO_API_KEY')
YAHOO_API_HOST = "yahoo-finance15.p.rapidapi.com"


# 감정 분석 요청 바디 스키마 정의
class NewsText(BaseModel):
    news_text: str


# 영어 감정 분석
def analyze_sentiment_english(news_text):
    api_url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    data = {"inputs": news_text}

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 200:
        sentiment_data = response.json()
        labels = {"negative": "negative", "neutral": "neutral", "positive": "positive"}

        if not sentiment_data or not sentiment_data[0]:
            return "Unknown"

        # 가장 높은 점수를 받은 감정 선택
        best_label = max(sentiment_data[0], key=lambda x: x["score"])["label"]
        sentiment_label = labels.get(best_label, "Unknown")
        return sentiment_label
    else:
        return "Unknown"


def analyze_sentiment_korean(news_text):
    api_url = "https://api-inference.huggingface.co/models/snunlp/KR-FinBert-SC"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    data = {"inputs": news_text}

    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code != 200:
        return "Unknown"

    content_type = response.headers.get("Content-Type", "")
    if "application/json" not in content_type:
        return "Unknown"

    try:
        sentiment_data = response.json()
    except Exception as e:
        logger.warning("JSON parse error: %s", e)
        return "Unknown"

    if not sentiment_data or not sentiment_data[0]:
        return "Unknown"

    # max() 로 label 고르기
    best_label = max(sentiment_data[0], key=lambda x: x["score"])["label"]
    label_map = {"positive": "positive", "negative": "negative", "neutral": "neutral"}
    return label_map.get(best_label, "Unknown")


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
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        news_data = response.json()

        # 응답 데이터가 예상한 구조인지 확인
        if "body" in news_data and isinstance(news_data["body"], list) and len(news_data["body"]) > 0:
            for article in news_data["body"]:
                description = article.get("description", "No description")

                # 감정 분석 수행
                sentiment = analyze_sentiment_english(description)
                if sentiment not in sentiment_counts:
                    sentiment_counts[sentiment] = 0
                sentiment_counts[sentiment] += 1

                # 감정 분석 결과를 뉴스 항목에 추가
                article["sentiment"] = sentiment

            return {
                "symbol": symbol,
                "sentiment_counts": sentiment_counts,
                "news": news_data["body"]
            }

        else:
            return {"error": "No news data available"}

    return {"error": "Failed to fetch"}


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

    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

    for article in articles[:20]:
        title = article.select_one("a.news_tit").text
        link = article.select_one("a.news_tit").get("href")
        description = article.select_one(".news_dsc").text if article.select_one(".news_dsc") else "No description"

        # 개별 기사 페이지 요청
        article_response = requests.get(link, headers=headers)
        article_soup = BeautifulSoup(article_response.text, "html.parser")

        # guid 역할 해줄 gdid 가져오기
        gdid_element = article_soup.find("meta", {"property": "nv:news:article:gid"})
        gdid = gdid_element["content"] if gdid_element else link

        # 발행일 가져오기
        pub_date_element = article_soup.find("meta", {"property": "article:published_time"})
        pub_date_raw = pub_date_element["content"] if pub_date_element else None

        if pub_date_raw:
            if pub_date_raw.endswith("Z"):
                pub_date_raw = pub_date_raw.replace("Z", "+00:00")
            try:
                pub_date_kr = datetime.fromisoformat(pub_date_raw)
            except ValueError:
                # 날짜 파싱 실패 시 처리
                pub_date_kr = "Invalid date format"
        else:
            pub_date_kr = "No Date information"

        # 감정 분석
        sentiment = analyze_sentiment_korean(description)
        sentiment_counts[sentiment] += 1

        news_list.append({
            "description": description,
            "guid": gdid,
            "link": link,
            "pubDate": pub_date_kr,
            "title": title,
            "sentiment": sentiment
        })

    return {"symbol": symbol, "news": news_list}



