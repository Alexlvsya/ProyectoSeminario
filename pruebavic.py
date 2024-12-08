import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Configuración global para Streamlit
st.set_page_config(
    page_title="Análisis de VaR/CVaR para ETFs",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos personalizados con CSS
st.markdown(
    """
    <style>
        .main {
            background-color: #001f3f; /* Azul marino */
            color: white;
        }
        .sidebar .sidebar-content {
            background-color: #003366; /* Azul más oscuro */
        }
        .css-1lcbmhc, .css-1x8cf1d, .css-2trqyj { 
            color: white; /* Texto en la barra lateral */
        }
        .css-17eq0hr a {
            color: #66ccff; /* Links */
        }
        .dataframe tr:hover {
            background-color: #112b47; /* Resaltar filas al pasar el mouse */
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Función para calcular CVaR
def calculate_cvar(returns, alpha=0.05):
    var = np.percentile(returns, 100 * alpha)
    cvar = returns[returns <= var].mean()
    return cvar

# Descargar datos de los ETFs
def obtener_datos(etfs, start_date, end_date):
    data = yf.download(etfs, start=start_date, end=end_date)["Adj Close"]
    daily_returns = data.pct_change() * 100  # Rendimientos en %
    return data, daily_returns

# Configurar parámetros
etfs = ["EMB", "XLE", "SPXL", "EEM", "SHV"]
start_date = "2010-01-01"
end_date = "2023-12-31"

# Descargar datos
data, daily_returns = obtener_datos(etfs, start_date, end_date)

# Calcular métricas
metrics = {}
risk_free_rate = 0.00116 / 252  # Tasa libre de riesgo diaria

for etf in etfs:
    etf_returns = daily_returns[etf].dropna()

    # Calcular métricas
    mean = etf_returns.mean()
    skewness = etf_returns.skew()
    kurtosis = etf_returns.kurtosis()
    var = np.percentile(etf_returns, 5)
    cvar = calculate_cvar(etf_returns)
    sharpe_ratio = (mean - risk_free_rate) / etf_returns.std()
    downside_returns = etf_returns[etf_returns < 0]
    sortino_ratio = (mean - risk_free_rate) / downside_returns.std()

    # Guardar métricas en el diccionario
    metrics[etf] = {
        "Mean": mean,
        "Skewness": skewness,
        "Excess Kurtosis": kurtosis,
        "VaR (95%)": var,
        "CVaR (95%)": cvar,
        "Sharpe Ratio": sharpe_ratio,
        "Sortino Ratio": sortino_ratio,
    }

metrics_df = pd.DataFrame(metrics).T.round(4)

# Función para graficar CVaR/VaR
def graficar_var_cvar(etf, returns):
    etf_returns = returns[etf].dropna()
    var = np.percentile(etf_returns, 5)
    cvar = calculate_cvar(etf_returns)

    plt.figure(figsize=(12, 6))
    plt.plot(etf_returns.index, etf_returns, color="#2C3E50", label=f'Daily Returns - {etf}')
    plt.fill_between(etf_returns.index, etf_returns, color='#2C3E50', alpha=0.1)
    plt.axhline(y=var, color='red', linestyle='--', linewidth=1.5, label=f'VaR (95%): {var:.2f}%')
    plt.axhline(y=cvar, color='green', linestyle='--', linewidth=1.5, label=f'CVaR (95%): {cvar:.2f}%')

    # Configuración de diseño
    plt.title(f'VaR/CVaR para {etf}', fontsize=18, weight='bold')
    plt.xlabel('Fecha', fontsize=14)
    plt.ylabel('Rendimiento (%)', fontsize=14)
    plt.legend(loc="upper left", frameon=True, shadow=True)
    plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.gca().set_facecolor('lightgray')
    plt.tight_layout()
    return plt

# Streamlit UI
st.title("Metrics for ETFs")

# Barra lateral
st.sidebar.header("ETFs")

# Selector de ETF
etf_seleccionado = st.sidebar.selectbox(
    "Select an ETF:",
    etfs,
    help="Choose an ETF to visualize its graphs and metrics"
)

# Mostrar gráfica del ETF seleccionado
st.subheader(f"Var/CVaR plot for {etf_seleccionado}")
grafica = graficar_var_cvar(etf_seleccionado, daily_returns)
st.pyplot(grafica)

# Mostrar tabla con métricas
st.subheader("Metrics for each ETF")
st.dataframe(metrics_df.style.background_gradient(cmap="Blues"))

