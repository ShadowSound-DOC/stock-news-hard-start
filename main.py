"""Stock news alerter — Alpha Vantage price move + NewsAPI headlines via Twilio SMS."""
import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

STOCK = os.getenv("STOCK", "TSLA")
COMPANY_NAME = os.getenv("COMPANY_NAME", "Tesla Inc")
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

ALPHA_API_KEY = os.environ["ALPHA_API_KEY"]
NEWS_API_KEY = os.environ["NEWS_API_KEY"]
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_FROM = os.environ["TWILIO_FROM"]
TWILIO_TO = os.environ["TWILIO_TO"]

alpha_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": ALPHA_API_KEY,
}
response = requests.get(url=STOCK_ENDPOINT, params=alpha_params, timeout=30)
response.raise_for_status()
data = response.json()
series = data.get("Time Series (Daily)")
if not series:
    raise SystemExit(f"Unexpected Alpha Vantage response: {data}")

# Use the two most recent trading days present in the feed
sorted_days = sorted(series.keys(), reverse=True)
latest_day, previous_day = sorted_days[0], sorted_days[1]
latest_close = float(series[latest_day]["4. close"])
previous_close = float(series[previous_day]["4. close"])
diff = latest_close - previous_close
pct = (diff / previous_close) * 100
direction = "UP" if diff >= 0 else "DOWN"
print(f"{STOCK} {direction} {abs(pct):.2f}% ({previous_day} -> {latest_day})")

if abs(pct) < 5:
    print("Move under 5%; no news/SMS.")
    raise SystemExit(0)

news_params = {
    "apiKey": NEWS_API_KEY,
    "q": COMPANY_NAME,
    "from": previous_day,
    "language": "en",
    "sortBy": "relevancy",
    "pageSize": 3,
}
news = requests.get(url=NEWS_ENDPOINT, params=news_params, timeout=30).json()
articles = (news.get("articles") or [])[:3]
if not articles:
    print("No articles found.")
    raise SystemExit(0)

client = Client(account_sid, auth_token)
for article in articles:
    headline = article.get("title") or ""
    brief = article.get("description") or ""
    body = (
        f"{STOCK}: {direction} {abs(pct):.0f}%\n"
        f"Headline: {headline}\n"
        f"Brief: {brief}"
    )
    message = client.messages.create(from_=TWILIO_FROM, body=body, to=TWILIO_TO)
    print(f"Sent SMS sid={message.sid}")
