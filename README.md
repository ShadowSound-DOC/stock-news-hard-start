# Stock News Hard Start

Checks Alpha Vantage daily closes for a stock. If the move is ≥ 5%, fetches top NewsAPI headlines and texts them via Twilio.

## Setup
1. Copy `.env.example` → `.env` and fill Alpha Vantage, NewsAPI, and Twilio values.
2. `pip install requests twilio python-dotenv`

## Run
```
python main.py
```
