import pandas as pd
import yfinance as yf

def get_stock_price(symbol: str):
    """
    Récupère le dernier prix et les infos du jour pour un actif donné.
    """
    try:
        # Nettoyage du symbole (majuscule, sans espaces)
        symbol = symbol.upper().strip()
        ticker = yf.Ticker(symbol)
        
        # history(period="1d") est plus rapide et propre que download
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
        print(f"Erreur lors de la récupération du prix pour {symbol}: {e}")
        return None

def get_historical_data(symbol: str, period="1y", interval="1d"):
    """
    Récupère l'historique des cours (Open, High, Low, Close, Volume).
    """
    try:
        symbol = symbol.upper().strip()
        ticker = yf.Ticker(symbol)
        
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            return pd.DataFrame()
            
        # Suppression de la timezone (UTC-5 etc) qui pose souvent problème avec les graphiques
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        # IMPORTANT : On remet la Date en tant que colonne pour éviter le bug
        df = df.reset_index()
        
        # Renommage optionnel pour être sûr (yfinance met "Date", certains codes cherchent "time")
        # On garde "Date" par défaut car c'est le standard yfinance    
        return df
        
    except Exception as e:
        print(f"Erreur lors de la récupération de l'historique pour {symbol}: {e}")
        return pd.DataFrame()