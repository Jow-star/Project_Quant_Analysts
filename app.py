import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from data_fetcher import get_stock_price, get_historical_data
from single_asset import moving_average_strategy, predict_next_close
from portfolio import simulate_portfolio, correlation_matrix, volatility, portfolio_performance
from utils import plot_price, plot_strategy
from config import ASSETS, REFRESH_INTERVAL

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
    st.markdown(f"**Actifs du portefeuille :** {', '.join(ASSETS)}")
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
# ONGLET 1 : ANALYSE D'UN ACTIF
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["🔍 Analyse d'un actif", "📦 Portefeuille multi‑actifs"])

with tab1:
    st.header("🔍 Analyse d'un actif")

    c1, c2 = st.columns([3, 1])
    with c1:
        symbol = st.text_input(
            "Symbole de l’actif",
            value="AAPL",
            placeholder="Ex : AAPL, MSFT, GOOGL, TSLA…",
        )
    with c2:
        analyze = st.button("Analyser", use_container_width=True)

    if analyze and symbol.strip():
        symbol = symbol.upper().strip()

        with st.spinner(f"Récupération des données pour {symbol}…"):
            price_info = get_stock_price(symbol)

        if price_info is None:
            st.error(f"Impossible de récupérer les données pour {symbol}.")
        else:
            # ---- Métriques du jour ----
            st.subheader(f"📊 Données du jour — {symbol}")
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                delta = 0
                if price_info["open"]:
                    delta = (price_info["current"] - price_info["open"]) / price_info["open"] * 100
                st.metric(
                    "Prix actuel",
                    f"{price_info['current']:.2f} USD",
                    f"{delta:+.2f} %",
                )

            with c2:
                st.metric("Plus haut (jour)", f"{price_info['high']:.2f} USD")

            with c3:
                st.metric("Plus bas (jour)", f"{price_info['low']:.2f} USD")

            with c4:
                st.metric("Ouverture", f"{price_info['open']:.2f} USD")

            st.divider()

            # ---- Données historiques ----
            with st.spinner("Chargement des données historiques…"):
                df = get_historical_data(symbol, period="6mo", interval="1d")

            if df.empty or "Date" not in df.columns or "Close" not in df.columns:
                st.error("Aucune donnée historique exploitable.")
            else:
                # Graphique des prix
                st.subheader("📈 Historique des prix")
                try:
                    fig = plot_price(df, title=f"Historique des prix — {symbol}")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur lors de l'affichage du graphique : {e}")

                st.divider()

                # ---- Stratégie SMA ----
                st.subheader("📊 Stratégie de moyennes mobiles (SMA)")
                s1, s2 = st.columns(2)
                with s1:
                    short_w = st.slider("Fenêtre courte (jours)", 5, 50, 20)
                with s2:
                    long_w = st.slider("Fenêtre longue (jours)", 50, 200, 50)

                try:
                    df_sma = moving_average_strategy(df.copy(), short_w, long_w)
                    fig_sma = plot_strategy(
                        df_sma, title=f"SMA {short_w}/{long_w} — {symbol}"
                    )
                    st.plotly_chart(fig_sma, use_container_width=True)

                    last_sig = df_sma["signal"].iloc[-1]
                    if last_sig == 1:
                        st.success("Signal actuel : **ACHAT** (SMA courte > SMA longue).")
                    elif last_sig == -1:
                        st.warning("Signal actuel : **VENTE** (SMA courte < SMA longue).")
                    else:
                        st.info("Signal actuel : **NEUTRE**.")
                except Exception as e:
                    st.error(f"Erreur dans la stratégie SMA : {e}")

                st.divider()

                # ---- Prédiction du prochain cours ----
                st.subheader("🔮 Prédiction du prochain prix de clôture")
                try:
                    pred_price = predict_next_close(df.copy())
                    last_close = df["Close"].iloc[-1]
                    var_pred = 0
                    if last_close:
                        var_pred = (pred_price - last_close) / last_close * 100

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("Prix prédit", f"{pred_price:.2f} USD")
                    with c2:
                        st.metric("Dernier cours", f"{last_close:.2f} USD")
                    with c3:
                        st.metric("Variation estimée", f"{var_pred:+.2f} %")
                    st.caption(
                        "Attention : simple régression linéaire sur les prix passés, "
                        "à utiliser uniquement à titre indicatif."
                    )
                except Exception as e:
                    st.error(f"Erreur lors de la prédiction : {e}")

                st.divider()

                # ---- Tableau des données ----
                st.subheader("📋 Données historiques (dernières lignes)")
                with st.expander("Voir les 10 derniers jours"):
                    show_cols = [c for c in ["Date", "Open", "High", "Low", "Close", "Volume"] if c in df.columns]
                    tmp = df[show_cols].tail(10).copy()
                    if "Date" in tmp.columns:
                        tmp["Date"] = pd.to_datetime(tmp["Date"]).dt.strftime("%Y-%m-%d")
                    st.dataframe(tmp, use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# ONGLET 2 : PORTEFEUILLE MULTI‑ACTIFS
# ---------------------------------------------------------
with tab2:
    st.header("📦 Portefeuille multi‑actifs")
    st.write(f"Actifs définis dans `config.py` : {', '.join(ASSETS)}")

    with st.spinner("Chargement des données du portefeuille…"):
        prices_dict = {}
        infos = []

        for asset in ASSETS:
            pi = get_stock_price(asset)
            if pi is not None:
                infos.append(
                    {
                        "Actif": asset,
                        "Prix actuel": pi["current"],
                        "Haut": pi["high"],
                        "Bas": pi["low"],
                    }
                )
            df_asset = get_historical_data(asset, period="6mo", interval="1d")
            if not df_asset.empty and "Close" in df_asset.columns:
                prices_dict[asset] = df_asset["Close"]
            else:
                st.warning(f"Aucune donnée exploitable pour {asset}.")

    if not prices_dict:
        st.error("Aucune donnée historique disponible pour le portefeuille.")
    else:
        # Tableau des prix actuels
        if infos:
            st.subheader("💰 Prix actuels des actifs")
            df_infos = pd.DataFrame(infos)
            st.dataframe(df_infos, use_container_width=True, hide_index=True)
            st.divider()

        # Poids égaux
        n = len(prices_dict)
        weights = [1 / n] * n

        # Performance du portefeuille
        st.subheader("📈 Performance du portefeuille")
        try:
            perf = portfolio_performance(prices_dict, weights)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Rendement total", f"{perf['total_return']:.2f} %")
            with c2:
                st.metric("Rendement annualisé", f"{perf['annual_return']:.2f} %")
            with c3:
                st.metric("Volatilité", f"{perf['volatility']:.2f} %")
            with c4:
                st.metric("Sharpe ratio", f"{perf['sharpe_ratio']:.2f}")
        except Exception as e:
            st.error(f"Erreur lors du calcul des performances : {e}")
        st.divider()

        # Courbe de performance cumulée
        st.subheader("📊 Évolution cumulée du portefeuille")
        try:
            port_ret = simulate_portfolio(prices_dict, weights)
            cum = (1 + port_ret).cumprod() - 1
            chart_df = pd.DataFrame({"Rendement cumulatif (%)": cum * 100})
            st.line_chart(chart_df, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur sur la courbe de performance : {e}")
        st.divider()

        # Corrélation
        st.subheader("🔗 Corrélation entre les actifs")
        try:
            corr = correlation_matrix(prices_dict)
            st.dataframe(corr.round(3), use_container_width=True)
        except Exception as e:
            st.error(f"Erreur sur la matrice de corrélation : {e}")
        st.divider()

        # Volatilité par actif
        st.subheader("📉 Volatilité annualisée par actif")
        try:
            vol = volatility(prices_dict)
            vol_df = (vol * 100).round(2).rename("Volatilité (%)").reset_index()
            vol_df.columns = ["Actif", "Volatilité (%)"]
            st.dataframe(vol_df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Erreur sur la volatilité : {e}")

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()
st.caption(
    "Données fournies à titre indicatif uniquement, ne constituent pas un conseil en investissement."
)
