import pandas as pd
import numpy as np

def simulate_portfolio(prices_dict, weights=None):
    """Simule la performance d'un portefeuille pondéré"""
    # Concaténer les séries en DataFrame avec alignement des dates
    df = pd.concat(prices_dict.values(), axis=1, keys=prices_dict.keys())
    
    # Calculer les rendements quotidiens
    returns = df.pct_change().dropna()
    
    # Si aucun poids spécifié, poids égaux
    if weights is None:
        weights = [1/len(prices_dict)] * len(prices_dict)
    
    # Rendements pondérés du portefeuille
    portfolio_returns = (returns * weights).sum(axis=1)
    return portfolio_returns

def correlation_matrix(prices_dict):
    """Calcule la matrice de corrélation entre les actifs"""
    df = pd.concat(prices_dict.values(), axis=1)
    df.columns = prices_dict.keys()
    return df.pct_change().corr()

def volatility(prices_dict):
    """Calcule la volatilité annualisée (252 jours de trading/an)"""
    df = pd.concat(prices_dict.values(), axis=1)
    df.columns = prices_dict.keys()
    # Volatilité annualisée
    annual_volatility = df.pct_change().std() * np.sqrt(252)
    return annual_volatility

def portfolio_performance(prices_dict, weights):
    """
    Calcule les métriques de performance du portefeuille.
    
    Parameters:
    -----------
    prices_dict : dict
        Dictionnaire {symbol: Series de prix}
    weights : list
        Poids de chaque actif (doit sommer à 1)
    
    Returns:
    --------
    dict : {
        'total_return': rendement total en %,
        'annual_return': rendement annualisé en %,
        'volatility': volatilité annualisée en %,
        'sharpe_ratio': ratio de Sharpe (sans risque=0)
    }
    """
    # Rendements du portefeuille
    port_ret = simulate_portfolio(prices_dict, weights)
    
    # Rendement total
    total_return = (1 + port_ret).prod() - 1
    
    # Nombre de jours de trading par an
    trading_days = 252
    
    # Rendement annualisé
    nb_days = len(port_ret)
    annual_return = (1 + total_return) ** (trading_days / nb_days) - 1
    
    # Volatilité annualisée
    volatility_annual = port_ret.std() * np.sqrt(trading_days)
    
    # Sharpe ratio (sans taux sans risque)
    sharpe_ratio = annual_return / volatility_annual if volatility_annual > 0 else 0
    
    return {
        'total_return': total_return * 100,
        'annual_return': annual_return * 100,
        'volatility': volatility_annual * 100,
        'sharpe_ratio': sharpe_ratio
    }