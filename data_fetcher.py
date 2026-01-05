import requests
import pandas as pd
import yfinance as yf
# import time
# from config import FINNHUB_API_KEY

# def get_stock_price(symbol: str):
#     url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
#     response = requests.get(url).json()
#     return {
#         "current": response.get("c"),
#         "high": response.get("h"),
#         "low": response.get("l"),
#         "open": response.get("o")
#     }

# def get_historical_data(symbol: str, resolution="D", count=200):
#     url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution={resolution}&count={count}&token={FINNHUB_API_KEY}"
#     data = requests.get(url).json()
#     df = pd.DataFrame({"time": data["t"], "open": data["o"], "high": data["h"], "low": data["l"], "close": data["c"]})
#     df["time"] = pd.to_datetime(df["time"], unit="s")
#     return df


# def get_historical_data(symbol: str, resolution="1", days=30):
#     to_ts = int(time.time())  # maintenant
#     from_ts = to_ts - days * 24 * 60 * 60  # X jours en arrière
#     url = f"https://finnhub.io/api/v1/stock/candle?symbol={symbol}&resolution={resolution}&from={from_ts}&to={to_ts}&token={FINNHUB_API_KEY}"
#     data = requests.get(url).json()

#     if data.get("s") != "ok":
#         return pd.DataFrame(columns=["time", "open", "high", "low", "close"])  # pas de données

#     lengths = list(map(len, [data["t"], data["o"], data["h"], data["l"], data["c"]]))
#     min_len = min(lengths)

#     if min_len == 0:
#         return pd.DataFrame(columns=["time", "open", "high", "low", "close"])
    
#     df = pd.DataFrame({
#         "time": data["t"][:min_len],
#         "open": data["o"][:min_len],
#         "high": data["h"][:min_len],
#         "low": data["l"][:min_len],
#         "close": data["c"][:min_len]
#     })
#     df["time"] = pd.to_datetime(df["time"], unit="s")


def get_stock_price(symbol: str):
    try:
        yf.pdr_override()
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if data.empty:
            return None
        return {
            "current": round(data["Close"].iloc[-1], 2),
            "high": round(data["High"].iloc[-1], 2),
            "low": round(data["Low"].iloc[-1], 2),
            "open": round(data["Open"].iloc[-1], 2)
        }
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def get_historical_data(symbol: str, period="6mo", interval="1d"):
    df = yf.download(symbol, period=period, interval=interval)
    if df.empty:
        return pd.DataFrame()
    df.reset_index(inplace=True)
    return df
