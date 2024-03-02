import requests
from datetime import datetime, timedelta
from twilio.rest import Client
import os

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
MY_PHONE_NUMBER = os.environ.get("PHONE_NUMBER")
news_api_key = os.environ.get("NEWS_API_KEY")
stock_market_api_key = os.environ.get("STOCK_MARKET_API_KEY")

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

# Twilio account
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
twilio_number = os.environ.get("TWILIO_NUMBER")

# Step 1: Stock Price Api
# Use https://newsapi.org/v2/everything?q=tesla&from=2023-11-10&to=2023-11-10&sortBy
# =popularity&apiKey=fd0459b3de4347ceaf8fd272a0092216

stock_message = ""
stock_market_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": stock_market_api_key
}

stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_market_parameters)
stock_response.raise_for_status()
data = stock_response.json()["Time Series (Daily)"]
data_list = [value for (key, value) in data.items()]

yesterday_data = data_list[0]
yesterday_closing_price = float(yesterday_data["4. close"])

previous_day_data = data_list[1]
previous_day_data_closing_price = float(previous_day_data["4. close"])

difference = abs(yesterday_closing_price - previous_day_data_closing_price)

diff_percent = round((difference / yesterday_closing_price) * 100)

# Step 2: News Apı:
# Use https://newsapi.org/v2/everything?q=apple&from=2023-11-10&to=2023-11-10&sortBy=popularity&apiKey=fd0459b3de4347ceaf8fd272a0092216
# Use https://newsapi.org/docs/endpoints/everything
if diff_percent > 1:
    news_api_paramaters = {
        "q": COMPANY_NAME,
        "sortBy": "popularity",
        "apiKey": news_api_key,
        "searchIn": "title",
        "language": "en"
    }

    news_response = requests.get(url=NEWS_ENDPOINT, params=news_api_paramaters)
    news_response.raise_for_status()
    articles = news_response.json()["articles"]

    three_articles = articles[:3]

    news_source = articles[0]["source"]["name"]
    news_title = articles[0]["title"]
    news_description = articles[0]["description"]

    if yesterday_closing_price > previous_day_data_closing_price:
        stock_message = f"{STOCK}: 🔺{diff_percent}%"
    else:
        stock_message = f"{STOCK}: 🔻{diff_percent}%"

    Message = f"{stock_message}\nHeadline: {news_title}.\nBrief: {news_description}.\n{news_source}"

    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body=Message,
        from_=twilio_number,
        to=MY_PHONE_NUMBER
    )
