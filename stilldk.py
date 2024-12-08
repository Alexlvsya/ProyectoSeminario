#Análisis de DRAWDOWN 

import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

def obtener_datos_acciones(simbolos, start_date, end_date):
    """Descarga datos históricos de precios"""
    data = yf.download(simbolos, start=start_date, end=end_date)['Close']
    return data.ffill().dropna()

def calcular_drawdown(precios):
    """Calcula el drawdown y high water mark"""
    high_water_mark = precios.expanding().max()
    drawdown = (precios - high_water_mark) / high_water_mark
    return drawdown, high_water_mark

def graficar_drawdown_financiero(precios, titulo="Análisis de Drawdown"):
    """Crea gráfico de precios y drawdown en subplots"""
    drawdown, hwm = calcular_drawdown(precios)

    # Crear figura con subplots
    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3])

    # Subplot 1: Precios y HWM
    fig.add_trace(
        go.Scatter(
            x=precios.index,
            y=precios.values,
            name='Precio',
            line=dict(color='#6A5ACD'),
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=hwm.index,
            y=hwm.values,
            name='High Water Mark',
            line=dict(color='green', dash='dash'),
        ),
        row=1, col=1
    )

    # Subplot 2: Drawdown
    fig.add_trace(
        go.Scatter(
            x=drawdown.index,
            y=drawdown.values,
            name='Drawdown',
            line=dict(color='red'),
            fill='tozeroy',
            fillcolor='rgba(255,0,0,0.1)'
        ),
        row=2, col=1
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
        opacity=0.5,
        row=2
    )

    # Actualizar layout
    fig.update_layout(
        title=titulo,
        height=800,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        hovermode='x unified'
    )

    # Actualizar ejes Y
    fig.update_yaxes(title="Precio", row=1, col=1)
    fig.update_yaxes(
        title="Drawdown %",
        tickformat=".1%",
        range=[-1, 0.1],
        row=2,
        col=1
    )
    fig.update_xaxes(title="Fecha", row=2, col=1)

    return fig

def obtener_max_drawdown_info(precios):
    """Obtiene información detallada del máximo drawdown"""
    drawdown, _ = calcular_drawdown(precios)

    max_drawdown = drawdown.min()
    fecha_max_drawdown = drawdown.idxmin()
    pico_anterior = precios[:fecha_max_drawdown].idxmax()

    datos_posteriores = drawdown[fecha_max_drawdown:]
    fechas_recuperacion = datos_posteriores[datos_posteriores >= 0]
    fecha_recuperacion = fechas_recuperacion.index[0] if len(fechas_recuperacion) > 0 else None

    duracion_caida = (fecha_max_drawdown - pico_anterior).days
    duracion_recuperacion = (fecha_recuperacion - fecha_max_drawdown).days if fecha_recuperacion else None
    duracion_total = (fecha_recuperacion - pico_anterior).days if fecha_recuperacion else None

    return {
        'max_drawdown': max_drawdown * 100,
        'fecha_pico': pico_anterior,
        'fecha_valle': fecha_max_drawdown,
        'fecha_recuperacion': fecha_recuperacion,
        'duracion_caida': duracion_caida,
        'duracion_recuperacion': duracion_recuperacion,
        'duracion_total': duracion_total
    }

# Configurar Streamlit
st.set_page_config(page_title="Análisis de ETFs", layout="wide")

st.title("Análisis de Drawdown y Rendimiento de ETFs")

# Parámetros iniciales
simbolos = ["EMB", "XLE", "SPXL", "EEM", "SHV"]
start_date = '2010-01-01'
end_date = datetime.now()

# Obtener datos
datos = obtener_datos_acciones(simbolos, start_date, end_date)

# Selección del ETF
etf_seleccionado = st.selectbox(
    "Selecciona un ETF para analizar:",
    options=simbolos,
    format_func=lambda x: f"{x} (ETF)",
    help="Selecciona el ETF para visualizar su análisis y gráficos."
)

# Procesar datos del ETF seleccionado
precios = datos[etf_seleccionado]
fig = graficar_drawdown_financiero(precios, f'Análisis de Drawdown - {etf_seleccionado}')
info_dd = obtener_max_drawdown_info(precios)

# Mostrar gráficos y análisis
st.plotly_chart(fig, use_container_width=True)

st.subheader(f"Análisis de Drawdown para {etf_seleccionado}")
st.write(f"**Máximo Drawdown:** {info_dd['max_drawdown']:.2f}%")
st.write(f"**Fecha del pico:** {info_dd['fecha_pico'].strftime('%Y-%m-%d')}")
st.write(f"**Fecha del valle:** {info_dd['fecha_valle'].strftime('%Y-%m-%d')}")
st.write(f"**Duración de la caída:** {info_dd['duracion_caida']} días")

if info_dd['fecha_recuperacion']:
    st.write(f"**Fecha de recuperación:** {info_dd['fecha_recuperacion'].strftime('%Y-%m-%d')}")
    st.write(f"**Duración de la recuperación:** {info_dd['duracion_recuperacion']} días")
    st.write(f"**Duración total:** {info_dd['duracion_total']} días")
else:
    st.write("El activo aún no se ha recuperado del máximo drawdown.")



#Analisis de Var/CVaR


import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

# Configuración global para Streamlit
st.set_page_config(page_title="Análisis de VaR/CVaR para ETFs", layout="wide")

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
    plt.title(f'VaR/CVaR for {etf}', fontsize=18, weight='bold')
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Return (%)', fontsize=14)
    plt.legend(loc="upper left", frameon=True, shadow=True)
    plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
    plt.gca().set_facecolor('lightgray')
    plt.tight_layout()
    return plt

# Streamlit UI
st.title("Análisis de VaR/CVaR para ETFs")
st.sidebar.header("Parámetros")

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
st.subheader("Tabla de métricas de todos los ETFs")
st.dataframe(metrics_df)