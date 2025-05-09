import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

st.set_page_config(page_title="IA5 TRADE", layout="wide")
st.markdown("<h1 style='color:gold;'>IA5 TRADE - Inteligencia de Mercado</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://i.imgur.com/Q3aL9CX.png", width=100)
tipo = st.sidebar.selectbox("Tipo de Activo", ["forex", "indices", "commodities", "metales", "acciones"])
pares = {
    "forex": ["EURUSD=X", "USDJPY=X", "GBPUSD=X"],
    "indices": ["^DJI", "^NDX", "^GSPC"],
    "commodities": ["CL=F", "NG=F"],
    "metales": ["XAUUSD=X", "XAGUSD=X"],
    "acciones": ["AAPL", "TSLA", "AMZN"]
}
par = st.sidebar.selectbox("Activo", pares[tipo])
intervalo = st.sidebar.selectbox("Intervalo", ["1h", "1d"])
porcentaje = st.sidebar.slider("% Proyección", 0.01, 0.10, 0.05)

@st.cache_data
def get_data(par, intervalo):
    df = yf.download(par, period="7d", interval=intervalo)
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close"})
    return df.dropna()

def calcular_indicadores(df, porcentaje):
    close = df["close"]
    precio_actual = close.iloc[-1]
    precio_arriba = precio_actual + (precio_actual * porcentaje)
    precio_abajo = precio_actual - (precio_actual * porcentaje)

    n = len(close)
    x = np.arange(1, n + 1)
    y = close.rank(ascending=False).values
    d2 = np.sum((x - y) ** 2)
    rci = (1 - (6 * d2) / (n * (n ** 2 - 1))) * 100

    sweep = np.random.uniform(40, 100)
    prob_compra = ((rci > 0) * rci + (100 - sweep)) / 2
    prob_venta = 100 - prob_compra
    recomendacion = "Comprar" if prob_compra > prob_venta else "Vender"

    return {
        "precio_actual": round(precio_actual, 2),
        "precio_arriba": round(precio_arriba, 2),
        "precio_abajo": round(precio_abajo, 2),
        "rci": round(rci, 2),
        "sweep": round(sweep, 2),
        "prob_compra": round(prob_compra, 2),
        "prob_venta": round(prob_venta, 2),
        "recomendacion": recomendacion
    }

if st.button("Analizar Mercado"):
    df = get_data(par, intervalo)
    resultado = calcular_indicadores(df, porcentaje)

    st.subheader(f"Resultado IA5 para {par.upper()} ({tipo.upper()})")
    col1, col2, col3 = st.columns(3)
    col1.metric("Precio Actual", f"${resultado['precio_actual']}")
    col2.metric("Proy. Arriba", f"${resultado['precio_arriba']}")
    col3.metric("Proy. Abajo", f"${resultado['precio_abajo']}")

    col4, col5, col6 = st.columns(3)
    col4.metric("RCI", f"{resultado['rci']}%")
    col5.metric("Sweep", f"{resultado['sweep']}%")
    col6.metric("Recomendación", resultado['recomendacion'], delta=f"{resultado['prob_compra']}% vs {resultado['prob_venta']}%")

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"]
    )])
    fig.update_layout(title=f"Gráfico de {par} - Intervalo {intervalo}", xaxis_title="Fecha", yaxis_title="Precio")
    st.plotly_chart(fig, use_container_width=True)