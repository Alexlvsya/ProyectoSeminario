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
            name='Value',
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
    fig.update_yaxes(title="Value", row=1, col=1)
    fig.update_yaxes(
        title="Drawdown %",
        tickformat=".1%",
        range=[-1, 0.1],
        row=2,
        col=1
    )
    fig.update_xaxes(title="Date", row=2, col=1)

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

st.title("ETFs Drawdown Analysis")

# Parámetros iniciales
simbolos = ["EMB", "XLE", "SPXL", "EEM", "SHV"]
start_date = '2010-01-01'
end_date = datetime.now()

# Obtener datos
datos = obtener_datos_acciones(simbolos, start_date, end_date)

# Selección del ETF
etf_seleccionado = st.selectbox(
    "Select an ETF to Analyze:",
    options=simbolos,
    format_func=lambda x: f"{x} (ETF)",
    help="Select one Etf to visualize its Drawdown Anlyisis and its graphs."
)

# Procesar datos del ETF seleccionado
precios = datos[etf_seleccionado]
fig = graficar_drawdown_financiero(precios, f'Drawdown Analyisis - {etf_seleccionado}')
info_dd = obtener_max_drawdown_info(precios)

# Mostrar gráficos y análisis
st.plotly_chart(fig, use_container_width=True)

st.subheader(f"Drawdown analysis for {etf_seleccionado}")
st.write(f"**Max Drawdown:** {info_dd['max_drawdown']:.2f}%")
st.write(f"**Peak Date:** {info_dd['fecha_pico'].strftime('%Y-%m-%d')}")
st.write(f"**Valley Date:** {info_dd['fecha_valle'].strftime('%Y-%m-%d')}")
st.write(f"**Decline Lenght:** {info_dd['duracion_caida']} days ")

if info_dd['fecha_recuperacion']:
    st.write(f"**Recovery Date:** {info_dd['fecha_recuperacion'].strftime('%Y-%m-%d')}")
    st.write(f"**Recovery Lenght:** {info_dd['duracion_recuperacion']} days")
    st.write(f"**Total Lenght:** {info_dd['duracion_total']} days")
else:
    st.write("Asset has not recovered yet from max drawdown.")