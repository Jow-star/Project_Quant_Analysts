import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime
import os

# Liste des actifs à surveiller pour le rapport automatique
# (On la met en dur ici car le rapport tourne en arrière-plan)
ASSETS = ["AAPL", "MSFT", "GOOGL", "TSLA", "BTC-USD"]

def calculate_max_drawdown(series):
    """Calcule la perte maximale historique sur la période donnée"""
    cum_max = series.cummax()
    drawdown = (series - cum_max) / cum_max
    return drawdown.min()

def generate_daily_report():
    print(f"--- Génération du rapport du {datetime.now()} ---")
    report_data = []
    
    for symbol in ASSETS:
        try:
            # On récupère 1 mois d'historique pour calculer la volatilité
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            
            if not hist.empty:
                # 1. Prix Open/Close du jour
                last_day = hist.iloc[-1]
                open_price = last_day["Open"]
                close_price = last_day["Close"]
                
                # 2. Volatilité (Ecart-type des rendements, annualisée)
                returns = hist["Close"].pct_change().dropna()
                volatility = returns.std() * np.sqrt(252) * 100
                
                # 3. Max Drawdown sur le dernier mois
                mdd = calculate_max_drawdown(hist["Close"]) * 100
                
                report_data.append({
                    "Actif": symbol,
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Open ($)": round(open_price, 2),
                    "Close ($)": round(close_price, 2),
                    "Volatilité Ann. (%)": round(volatility, 2),
                    "Max Drawdown 1M (%)": round(mdd, 2)
                })
                print(f"✅ {symbol} traité.")
            else:
                print(f"⚠️ Pas de données pour {symbol}")
                
        except Exception as e:
            print(f"❌ Erreur sur {symbol}: {e}")

    # Sauvegarde en CSV
    if report_data:
        df = pd.DataFrame(report_data)
        # Création d'un dossier 'reports' s'il n'existe pas
        if not os.path.exists("reports"):
            os.makedirs("reports")
            
        filename = f"reports/daily_report_{datetime.now().strftime('%Y-%m-%d')}.csv"
        df.to_csv(filename, index=False)
        print(f"📄 Rapport sauvegardé : {filename}")
    else:
        print("Aucune donnée à sauvegarder.")

if __name__ == "__main__":
    generate_daily_report()