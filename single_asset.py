import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression 

# --- 1. STRATÉGIE MOYENNES MOBILES (SMA) ---
def moving_average_strategy(df, short_window=20, long_window=50):
    """
    Stratégie croisement de moyennes mobiles.
    Génère les colonnes Cumulative_Market et Cumulative_Strategy.
    """
    df = df.copy()

    # Vérification que la colonne Close existe
    if "Close" not in df.columns:
        return df
    
    # Calcul des moyennes
    df["SMA_short"] = df["Close"].rolling(window=short_window).mean()
    df["SMA_long"] = df["Close"].rolling(window=long_window).mean()
    
    # Signal (1 = Achat, -1 = Vente)
    df["signal"] = 0
    df.loc[df["SMA_short"] > df["SMA_long"], "signal"] = 1
    df.loc[df["SMA_short"] < df["SMA_long"], "signal"] = -1
    
    # Calcul des rendements cumulés (INDISPENSABLE pour le graphique)
    # On décale le signal d'un jour pour simuler l'achat le lendemain
    df['Position'] = df['signal'].shift(1).fillna(0)
    
    df['Market_Returns'] = df['Close'].pct_change()
    df['Strategy_Returns'] = df['Market_Returns'] * df['Position']
    
    df['Cumulative_Market'] = (1 + df['Market_Returns']).cumprod() * 100
    df['Cumulative_Strategy'] = (1 + df['Strategy_Returns']).cumprod() * 100
    
    return df

# --- 2. STRATÉGIE RSI (MOMENTUM) ---
def rsi_strategy(df, window=14, lower_bound=30, upper_bound=70):
    """
    Stratégie RSI. Achat < 30, Vente > 70.
    Génère les colonnes Cumulative_Market et Cumulative_Strategy.
    """
    df = df.copy()
    
    if "Close" not in df.columns:
        return df

    # Calcul du RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Signal
    df['signal'] = 0
    df.loc[df['RSI'] < lower_bound, 'signal'] = 1  # Survente -> Achat
    df.loc[df['RSI'] > upper_bound, 'signal'] = -1 # Surachat -> Vente
    
    # Calcul des rendements cumulés
    # On garde la position jusqu'au prochain signal inverse (méthode simple : fillna avec ffill)
    # Note : pour simplifier, ici on prend juste le signal brut décalé, comme le SMA.
    df['Position'] = df['signal'].shift(1).fillna(0)
    
    # Petite astuce : si on veut rester en position tant qu'il n'y a pas de signal inverse
    # df['Position'] = df['signal'].replace(to_replace=0, method='ffill').shift(1).fillna(0)

    df['Market_Returns'] = df['Close'].pct_change()
    df['Strategy_Returns'] = df['Market_Returns'] * df['Position']
    
    df['Cumulative_Market'] = (1 + df['Market_Returns']).cumprod() * 100
    df['Cumulative_Strategy'] = (1 + df['Strategy_Returns']).cumprod() * 100
    
    return df

# --- 3. PRÉDICTION ML (Régression Linéaire) ---
def predict_next_close(df):
    """Prédit le prochain prix avec régression linéaire"""
    df_clean = df.dropna()
    
    # Sécurité
    if len(df_clean) < 2:
        return 0.0
    
    # Variables pour régression: X = temps, y = prix
    X = np.arange(len(df_clean)).reshape(-1, 1)
    y = df_clean["Close"].values
    
    # Entrainer le modèle
    model = LinearRegression()
    model.fit(X, y)
    
    # Prédire le prochain index
    next_index = [[len(df_clean)]]
    prediction = model.predict(next_index)
    
    # Retourne un float arrondi
    return round(float(prediction[0]), 2)

# --- 4. MÉTRIQUES DE RISQUE ---
def calculate_metrics(df):
    """
    Calcule les métriques de performance : Sharpe Ratio et Max Drawdown.
    """
    metrics = {}
    
    # Vérification
    if df is None or 'Strategy_Returns' not in df.columns:
        return None

    returns = df['Strategy_Returns']

    # 1. Ratio de Sharpe (Annualisé)
    mean_ret = returns.mean()
    volatility = returns.std()
    
    if volatility == 0 or np.isnan(volatility):
        metrics['Sharpe Ratio'] = 0.0
    else:
        metrics['Sharpe Ratio'] = (mean_ret / volatility) * np.sqrt(252)

    # 2. Max Drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    metrics['Max Drawdown'] = drawdown.min()
    
    return metrics