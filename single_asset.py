import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression 

def moving_average_strategy(df, short_window=20, long_window=50):
    df = df.copy()

    if "Close" not in df.columns:
        raise ValueError("La colonne 'Close' est manquante.")
    
    df["SMA_short"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_long"] = df["Close"].rolling(window=long_window).mean()
    df["signal"] = 0
    df.loc[df["SMA_short"] > df["SMA_long"], "signal"] = 1
    df.loc[df["SMA_short"] < df["SMA_long"], "signal"] = -1
    return df

# def predict_next_close(df):
#     df = df.dropna()
#     X = df.index.values.reshape(-1, 1)
#     y = df["Close"].values
#     model = LinearRegression().fit(X, y)
#     next_index = [[df.index[-1] + 1]]


def predict_next_close(df):
    """Prédit le prochain prix avec régression linéaire"""
    df_clean = df.dropna()
    
    # Sécurité
    if len(df_clean) < 2:
        return df_clean["Close"].iloc[-1] if not df_clean.empty else 0
    
    # Variables pour régression: X = temps, y = prix
    X = np.arange(len(df_clean)).reshape(-1, 1)  # [0, 1, 2, ..., n]
    y = df_clean["Close"].values  # 
    
    # Entrainer le modèle
    model = LinearRegression()
    model.fit(X, y)
    
    # Prédire le prochain index
    next_index = [[len(df_clean)]]
    prediction = model.predict(next_index)
    
    return round(prediction, 2)