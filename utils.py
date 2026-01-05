import plotly.graph_objects as go

# def plot_price(df, title="Prix de l'actif"):
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=df["time"], y=df["close"], mode="lines", name="Close"))
#     fig.update_layout(title=title, xaxis_title="Date", yaxis_title="Prix")
#     return fig



def plot_price(df, title="Prix de l'actif"):
    """Affiche le graphique du prix de clôture"""
    if df.empty:
        raise ValueError("DataFrame vide : aucune donnée disponible.")
    if "Date" not in df.columns or "Close" not in df.columns:
        raise ValueError("Les colonnes 'Date' et 'Close' sont requises dans le DataFrame.")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Close"],
        mode="lines",
        name="Close",
        line=dict(color="#1f77b4", width=2)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Prix (USD)",
        hovermode="x unified",
        template="plotly_white")
    
    return fig

def plot_strategy(df, title="Stratégie SMA"):
    """
    Affiche le graphique de la stratégie de moyennes mobiles.
    
    Parameters:
    -----------
    df : DataFrame
        DataFrame avec colonnes 'Date', 'Close', 'SMA_short', 'SMA_long', 'signal'
    title : str
        Titre du graphique
    
    Returns:
    --------
    go.Figure : Graphique Plotly
    """
    if df.empty:
        raise ValueError("DataFrame vide : aucune donnée disponible.")
    
    required_cols = ["Date", "Close", "SMA_short", "SMA_long"]
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Les colonnes requises sont : {required_cols}")
    
    fig = go.Figure()
    
    # Prix de clôture
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Close"],
        mode="lines",
        name="Prix",
        line=dict(color="#1f77b4", width=2)
    ))
    
    # SMA courte
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["SMA_short"],
        mode="lines",
        name="SMA Courte",
        line=dict(color="#ff7f0e", width=2, dash="dash")
    ))
    
    # SMA longue
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["SMA_long"],
        mode="lines",
        name="SMA Longue",
        line=dict(color="#2ca02c", width=2, dash="dash")
    ))
    
    # Zones d'achat (signal = 1) en vert clair
    buy_periods = df[df["signal"] == 1]
    if not buy_periods.empty:
        fig.add_vrect(
            x0=buy_periods.index.min(), x1=buy_periods.index.max(),
            fillcolor="green", opacity=0.1, layer="below", line_width=0,
            annotation_text="ACHAT"
        )
    
    # Zones de vente (signal = -1) en rouge clair
    sell_periods = df[df["signal"] == -1]
    if not sell_periods.empty:
        fig.add_vrect(
            x0=sell_periods.index.min(), x1=sell_periods.index.max(),
            fillcolor="red", opacity=0.1, layer="below", line_width=0,
            annotation_text="VENTE"
        )
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Prix (USD)",
        hovermode="x unified",
        template="plotly_white"
    )
    
    return fig
    