import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Import des modules locaux
from data_fetcher import get_stock_price, get_historical_data
from single_asset import moving_average_strategy, rsi_strategy, predict_next_close, calculate_metrics
from portfolio import simulate_portfolio, correlation_matrix, volatility, portfolio_performance
from utils import plot_price
from config import REFRESH_INTERVAL

# ---------------------------------------------------------
# CONFIGURATION GÉNÉRALE DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="📊 Dashboard Financier",
    page_icon="📈",
    layout="wide",
)

st.title("📊 Tableau de Bord Financier")
st.markdown("*Analyse en temps réel avec yfinance et Streamlit*")
st.divider()

# ---------------------------------------------------------
# BARRE LATERALE
# ---------------------------------------------------------
with st.sidebar:
    st.header("ℹ️ Informations")
    st.markdown(
        f"**Dernière mise à jour :** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )
    
    # CORRECTION : On ne lit plus ASSETS depuis config, c'est dynamique
    st.markdown("**Mode :** Sélection dynamique")
    
    st.markdown(f"**Rafraîchissement conseillé :** {REFRESH_INTERVAL // 60} minutes")

    st.divider()
    st.markdown(
        "### Guide rapide\n"
        "- Onglet 1 : Analyse d’un actif\n"
        "- Onglet 2 : Portefeuille multi‑actifs"
    )

    st.divider()
    if st.button("🔄 Rafraîchir la page", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ---------------------------------------------------------
# GESTION DES ONGLETS
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["🔍 Analyse d'un actif", "📦 Portefeuille multi‑actifs"])

# =========================================================
# ONGLET 1 : ANALYSE D'UN ACTIF (QUANT A)
# =========================================================
with tab1:
    st.header("🔍 Analyse d'un actif")

    c1, c2 = st.columns([3, 1])
    with c1:
        # On utilise session_state pour garder le symbole en mémoire si on change d'onglet
        symbol_input = st.text_input(
            "Symbole de l’actif",
            value="AAPL",
            placeholder="Ex : AAPL, MSFT, GOOGL, TSLA…",
        )

    with c2:
        # Gestion du bouton avec session_state pour éviter le refresh bug
        if st.button("Analyser", use_container_width=True):
            st.session_state["analyse_active"] = True
            st.session_state["symbol_analyzed"] = symbol_input

    # L'analyse se lance si le bouton a été cliqué une fois
    if st.session_state.get("analyse_active", False) and st.session_state.get("symbol_analyzed"):
        
        symbol = st.session_state["symbol_analyzed"].upper().strip()

        # 1. Récupération prix instantané
        with st.spinner(f"Récupération des données pour {symbol}…"):
            price_info = get_stock_price(symbol)

        if price_info is None:
            st.error(f"Impossible de récupérer les données pour {symbol}.")
        else:
            # ---- Métriques du jour ----
            st.subheader(f"📊 Données du jour — {symbol}")
            k1, k2, k3, k4 = st.columns(4)

            with k1:
                delta = 0
                if price_info["open"]:
                    delta = (price_info["current"] - price_info["open"]) / price_info["open"] * 100
                st.metric("Prix actuel", f"{price_info['current']:.2f} USD", f"{delta:+.2f} %")
            with k2:
                st.metric("Plus haut (jour)", f"{price_info['high']:.2f} USD")
            with k3:
                st.metric("Plus bas (jour)", f"{price_info['low']:.2f} USD")
            with k4:
                st.metric("Ouverture", f"{price_info['open']:.2f} USD")

            st.divider()

            # 2. Récupération Historique
            with st.spinner("Chargement des données historiques…"):
                df = get_historical_data(symbol, period="1y", interval="1d")

            if df.empty or "Date" not in df.columns or "Close" not in df.columns:
                st.error("Aucune donnée historique exploitable.")
            else:
                # Graphique des prix simples
                st.subheader("📈 Historique des prix")
                try:
                    fig = plot_price(df, title=f"Historique des prix — {symbol}")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur graphique : {e}")

                st.divider()

                # ---- 3. Backtesting de Stratégie ----
                st.subheader("🛠️ Backtesting de Stratégie")
                
                strategy_name = st.selectbox(
                    "Choisir la stratégie à tester :",
                    ["Moyennes Mobiles (SMA)", "RSI Momentum"]
                )

                df_strategy = None

                # Paramètres et Appel des fonctions
                if strategy_name == "Moyennes Mobiles (SMA)":
                    col1, col2 = st.columns(2)
                    short_w = col1.number_input("Fenêtre Courte", value=20, min_value=5)
                    long_w = col2.number_input("Fenêtre Longue", value=50, min_value=10)
                    
                    df_strategy = moving_average_strategy(df, short_w, long_w)

                elif strategy_name == "RSI Momentum":
                    col1, col2, col3 = st.columns(3)
                    rsi_window = col1.number_input("Période RSI", value=14)
                    rsi_low = col2.number_input("Seuil Achat (<)", value=30)
                    rsi_high = col3.number_input("Seuil Vente (>)", value=70)
                    
                    df_strategy = rsi_strategy(df, rsi_window, rsi_low, rsi_high)

                # Affichage des Résultats de la Stratégie
                if df_strategy is not None:
                    st.write(f"Comparaison : {strategy_name} vs Buy & Hold")
                    
                    # Graphique Comparatif (Base 100)
                    st.line_chart(df_strategy[['Cumulative_Market', 'Cumulative_Strategy']])
                    
                    # Performances Finales
                    perf_market = df_strategy['Cumulative_Market'].iloc[-1] - 100
                    perf_strat = df_strategy['Cumulative_Strategy'].iloc[-1] - 100
                    
                    c1, c2 = st.columns(2)
                    c1.metric("Performance Marché", f"{perf_market:.2f} %")
                    c2.metric(f"Performance {strategy_name}", f"{perf_strat:.2f} %")
                    
                    # Métriques de Risque (Sharpe / Drawdown)
                    metrics = calculate_metrics(df_strategy)
                    if metrics:
                        st.markdown("#### 📉 Indicateurs de Risque")
                        m1, m2 = st.columns(2)
                        m1.metric("Ratio de Sharpe", f"{metrics['Sharpe Ratio']:.2f}")
                        m2.metric("Max Drawdown", f"{metrics['Max Drawdown']:.2%}")
                
                st.divider()

                # ---- 4. Prédiction ML ----
                st.subheader("🔮 Prédiction du prochain prix de clôture")
                try:
                    pred_price = predict_next_close(df.copy())
                    last_close = df["Close"].iloc[-1]
                    var_pred = 0
                    if last_close:
                        var_pred = (pred_price - last_close) / last_close * 100

                    p1, p2, p3 = st.columns(3)
                    p1.metric("Prix prédit", f"{pred_price:.2f} USD")
                    p2.metric("Dernier cours", f"{last_close:.2f} USD")
                    p3.metric("Variation estimée", f"{var_pred:+.2f} %")
                    st.caption("Attention : simple régression linéaire, à titre indicatif.")
                except Exception as e:
                    st.error(f"Erreur prédiction : {e}")

                st.divider()

                # ---- 5. Données Brutes ----
                st.subheader("📋 Données historiques")
                with st.expander("Voir les dernières données"):
                    st.dataframe(df.tail(10), use_container_width=True, hide_index=True)


# =========================================================
# ONGLET 2 : PORTEFEUILLE MULTI‑ACTIFS (QUANT B)
# =========================================================
with tab2:
    st.header("📦 Portefeuille multi‑actifs")
    
    # 1. SÉLECTION DYNAMIQUE DES ACTIFS
    tickers_dispo = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "BTC-USD", "ETH-USD"]
    
    col_sel1, col_sel2 = st.columns([3, 1])
    with col_sel1:
        selected_assets = st.multiselect(
            "Composez votre portefeuille :",
            options=tickers_dispo,
            default=["AAPL", "MSFT", "GOOGL"]
        )
    
    # 2. SÉLECTION DES POIDS
    weights = []
    if not selected_assets:
        st.warning("Veuillez sélectionner au moins un actif.")
    else:
        st.write("⚖️ **Répartition du capital (Poids)**")
        cols = st.columns(len(selected_assets))
        poids_temp = {}
        
        # Inputs dynamiques pour les poids
        for i, asset in enumerate(selected_assets):
            with cols[i]:
                default_w = 1.0 / len(selected_assets)
                val = st.number_input(f"{asset} (%)", min_value=0.0, max_value=100.0, value=default_w*100, step=5.0)
                poids_temp[asset] = val / 100.0
        
        total_weight = sum(poids_temp.values())
        weights = [poids_temp[a] for a in selected_assets]
        
        if not (0.99 <= total_weight <= 1.01):
            st.warning(f"⚠️ La somme des poids est de {total_weight*100:.0f}%. Elle devrait faire 100%.")

        st.divider()

        # BOUTON LANCER L'ANALYSE
        if st.button("Simuler le Portefeuille", use_container_width=True):
            
            with st.spinner("Simulation en cours..."):
                # Récupération des données
                prices_dict = {}
                for asset in selected_assets:
                    # On prend 1 an pour une bonne simulation
                    df_tmp = get_historical_data(asset, period="1y") 
                    if not df_tmp.empty and "Close" in df_tmp.columns:
                        prices_dict[asset] = df_tmp["Close"]
                
                if not prices_dict:
                    st.error("Pas de données disponibles.")
                else:
                    # --- A. Métriques Globales ---
                    perf = portfolio_performance(prices_dict, weights)
                    
                    st.subheader("📈 Performance Globale")
                    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                    kpi1.metric("Rendement Total", f"{perf['total_return']:.2f} %")
                    kpi2.metric("Rendement Annuel", f"{perf['annual_return']:.2f} %")
                    kpi3.metric("Volatilité", f"{perf['volatility']:.2f} %")
                    kpi4.metric("Ratio de Sharpe", f"{perf['sharpe_ratio']:.2f}")
                    
                    st.divider()

                    # --- B. Graphique Comparatif ---
                    st.subheader("📊 Comparaison : Actifs vs Portefeuille (Base 100)")
                    
                    port_ret = simulate_portfolio(prices_dict, weights)
                    cumulative_port = (1 + port_ret).cumprod() * 100
                    
                    chart_data = pd.DataFrame({"Portefeuille": cumulative_port})
                    
                    # Ajout des actifs individuels normalisés
                    for asset, series in prices_dict.items():
                        aligned_series = series.loc[cumulative_port.index]
                        normalized_asset = (aligned_series / aligned_series.iloc[0]) * 100
                        chart_data[asset] = normalized_asset
                    
                    st.line_chart(chart_data)
                    st.caption("Comparaison en base 100 (le portefeuille et les actifs partent tous de 100).")

                    st.divider()

                    # --- C. Matrice de Corrélation & Volatilité ---
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("🔗 Matrice de Corrélation")
                        corr = correlation_matrix(prices_dict)
                        st.dataframe(corr, use_container_width=True)
                    
                    with c2:
                        st.subheader("📉 Volatilité par Actif")
                        vol = volatility(prices_dict)
                        df_vol = pd.DataFrame(vol * 100, columns=["Volatilité (%)"])
                        st.dataframe(df_vol, use_container_width=True)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()
st.caption(
    "Données fournies à titre indicatif uniquement, ne constituent pas un conseil en investissement."
)