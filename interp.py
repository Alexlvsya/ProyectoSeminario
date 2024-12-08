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

# Interpretations dictionary
interpretations = {
    "EMB": """
    - **Mean**: Minimal daily gains.
    - **Skewness**: Significant left tail indicates extreme negative returns.
    - **Excess Kurtosis**: Heavy-tailed distribution with frequent extreme events.
    - **VaR (95%)**: Maximum expected daily loss is 0.79%.
    - **CVaR (95%)**: Average loss during extreme downturns is 1.38%.
    - **Sharpe Ratio**: Minimal risk-adjusted returns.
    - **Sortino Ratio**: Slightly better downside risk management.
    """,
    "XLE": """
    - **Mean**: Moderate daily gains.
    - **Skewness**: Slight bias toward negative returns.
    - **Excess Kurtosis**: Occasional extreme price movements.
    - **VaR (95%)**: Maximum expected daily loss is 2.62%.
    - **CVaR (95%)**: Average loss during extreme downturns is 4.04%.
    - **Sharpe Ratio**: Poor risk-adjusted returns.
    - **Sortino Ratio**: Better downside risk performance.
    """,
    "SPXL": """
    - **Mean**: Strong growth potential with the highest daily return.
    - **Skewness**: Mild asymmetry toward losses.
    - **Excess Kurtosis**: Significant likelihood of extreme price movements.
    - **VaR (95%)**: Maximum expected daily loss is 5.01%.
    - **CVaR (95%)**: Average loss in extreme cases is 8.01%.
    - **Sharpe Ratio**: Moderate risk-adjusted returns.
    - **Sortino Ratio**: Good performance relative to downside risk.
    """,
    "EEM": """
    - **Mean**: Minimal growth potential.
    - **Skewness**: Mild bias toward negative returns.
    - **Excess Kurtosis**: Moderate tendency for large swings.
    - **VaR (95%)**: Maximum expected daily loss is 2.1%.
    - **CVaR (95%)**: Average loss during extreme downturns is 3.17%.
    - **Sharpe Ratio**: Poor risk-adjusted returns.
    - **Sortino Ratio**: Subpar performance for downside risk-adjusted returns.
    """,
    "SHV": """
    - **Mean**: Near-zero yield, reflecting stability.
    - **Skewness**: Slight bias toward positive returns.
    - **Excess Kurtosis**: Less extreme tail behavior compared to others.
    - **VaR (95%)**: Minimal downside risk with a daily loss of 0.02%.
    - **CVaR (95%)**: Negligible average loss during extreme events.
    - **Sharpe Ratio**: Exceptional performance for minimal risk.
    - **Sortino Ratio**: Outstanding downside risk-adjusted returns.
    """
}

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

# Barra lateral
st.sidebar.header("Parámetros 📌")

# Selector de ETF
etf_seleccionado = st.sidebar.selectbox(
    "Selecciona un ETF:",
    etfs,
    help="Elige un ETF para visualizar su gráfico de VaR/CVaR."
)

# Mostrar gráfica del ETF seleccionado
st.subheader(f"Gráfica de VaR/CVaR para {etf_seleccionado}")
grafica = graficar_var_cvar(etf_seleccionado, daily_returns)
st.pyplot(grafica)

# Mostrar tabla con métricas
st.subheader("Interpretación de métricas")
st.markdown(interpretations[etf_seleccionado], unsafe_allow_html=True)
