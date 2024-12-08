import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Función para obtener datos históricos de precios
def obtener_datos_acciones(simbolos, start_date, end_date = None):
    if end_date is None:
        end_date = datetime.now()
    data = yf.download(simbolos, start=start_date, end=end_date)['Close']
    return data.ffill().dropna()

# Función para calcular drawdown y su información clave
def calcular_drawdown(precios):
    high_water_mark = precios.expanding().max()
    drawdown = (precios - high_water_mark) / high_water_mark
    return drawdown, high_water_mark

def obtener_max_drawdown_info(precios):
    drawdown, _ = calcular_drawdown(precios)
    max_drawdown = drawdown.min()
    fecha_valle = drawdown.idxmin()
    fecha_pico = precios.loc[:fecha_valle].idxmax()
    duracion_caida = (fecha_valle - fecha_pico).days

    post_valle = precios.loc[fecha_valle:]
    fecha_recuperacion = post_valle[post_valle >= precios[fecha_pico]].first_valid_index()

    if fecha_recuperacion is not None:
        duracion_recuperacion = (fecha_recuperacion - fecha_valle).days
        duracion_total = (fecha_recuperacion - fecha_pico).days
    else:
        duracion_recuperacion = None
        duracion_total = None

    return {
        'max_drawdown': max_drawdown * 100,
        'fecha_pico': fecha_pico,
        'fecha_valle': fecha_valle,
        'duracion_caida': duracion_caida,
        'fecha_recuperacion': fecha_recuperacion,
        'duracion_recuperacion': duracion_recuperacion,
        'duracion_total': duracion_total
    }

# Función para graficar drawdown del portafolio
def graficar_drawdown_portafolio(precios, titulo="Drawdown del Portafolio"):
    drawdown, hwm = calcular_drawdown(precios)

    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        row_heights=[0.7, 0.3])

    fig.add_trace(
        go.Scatter(
            x=precios.index,
            y=precios.values,
            name='Portfolio Value',
            line=dict(color='blue'),
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

    fig.update_layout(
        title=titulo,
        height=800,
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        hovermode='x unified'
    )

    fig.update_yaxes(title="Value (100 Base)", row=1, col=1)
    fig.update_yaxes(title="Drawdown %", tickformat=".1%", range=[-1, 0.1], row=2, col=1)
    fig.update_xaxes(title="Date", row=2, col=1)

    return fig

# Función para calcular métricas del portafolio
def calcular_metricas_portafolio(precios, retornos, pesos, tasa_libre_riesgo=0.0116 / 252):
    rendimiento_anual = retornos.mean() * 252
    rendimiento_acumulado = (1 + retornos).prod() - 1
    volatilidad_anual = retornos.std() * np.sqrt(252)
    sharpe_ratio = (rendimiento_anual - tasa_libre_riesgo) / volatilidad_anual
    sortino_ratio = (rendimiento_anual - tasa_libre_riesgo) / retornos[retornos < 0].std()
    sesgo = retornos.skew()
    curtosis = retornos.kurtosis()
    var_95 = np.percentile(retornos, 5)
    cvar_95 = retornos[retornos <= var_95].mean()

    info_dd = obtener_max_drawdown_info(precios)

    metricas = {
        'Rendimiento Anual (%)': rendimiento_anual * 100,
        'Rendimiento Acumulado (%)': rendimiento_acumulado * 100,
        'Volatilidad Anual (%)': volatilidad_anual * 100,
        'Sharpe Ratio': sharpe_ratio,
        'Sortino Ratio': sortino_ratio,
        'Sesgo': sesgo,
        'Curtosis': curtosis,
        'VaR 95%': var_95,
        'CVaR 95%': cvar_95,
        'Máximo Drawdown (%)': info_dd['max_drawdown'],
        'Fecha Pico': info_dd['fecha_pico'],
        'Fecha Valle': info_dd['fecha_valle'],
        'Duración de la Caída (días)': info_dd['duracion_caida'],
        'Fecha Recuperación': info_dd['fecha_recuperacion'],
        'Duración Recuperación (días)': info_dd['duracion_recuperacion'],
        'Duración Total (días)': info_dd['duracion_total']
    }

    return metricas

# Parámetros de entrada
simbolos = ['EMB', 'XLE', 'SPXL', 'EEM', 'SHV']
start_date = '2021-01-01'
end_date = '2023-12-31'
pesos_1 = np.array([0.02, 0.0, 0.9991, 0.03, 0.04])
pesos_2 = np.array([0.0001, 0.0272, 0.2326, 0.7372, 0.00028])
pesos_3 = np.array([0.213934, 0.049223, 0.715274, -0.019618, 0.041187])
pesos_4 = np.array([0.2, 0.2, 0.2, 0.2, 0.2])
pesos_list = [pesos_1, pesos_2, pesos_3, pesos_4]

nombres_portafolios = [
    "Minimum Volatility Portfolio",
    "Max Sharpe Ratio Portfolio",
    "Minimum Volatility Portfolio with 10% objective (MXN)",
    "Equally-Weighted Portfolio"
]

precios = obtener_datos_acciones(simbolos, start_date)
retornos = precios.pct_change().dropna()

# Interfaz de Streamlit
st.title("Portafolio Backetesting Analysis")

tipo_vista = st.radio("Select Preferred View:", ("Individual Portfolio Analysis", "Returns against S&P500"))

if tipo_vista == "Individual Portfolio Analysis":
    portafolio_seleccionado = st.selectbox("Seleccione un portafolio:", nombres_portafolios)
    idx = nombres_portafolios.index(portafolio_seleccionado)
    pesos = pesos_list[idx]
    precios_portafolio = (retornos * pesos).sum(axis=1).cumsum()

    metricas = calcular_metricas_portafolio(precios_portafolio, retornos @ pesos, pesos)

    st.subheader(f"Metrics of  {portafolio_seleccionado}")
    st.markdown("""
    | Métrica                       | Valor                       |
    |-------------------------------|-----------------------------|
    | **Anual Return (%)**          | {:.2f}%                     |
    | **Cumulative Return  (%)**    | {:.2f}%                     |
    | **Anual Volatility (%)**      | {:.2f}%                     |
    | **Sharpe Ratio**              | {:.2f}                      |
    | **Sortino Ratio**             | {:.2f}                      |
    | **Skewness**                  | {:.2f}                      |
    | **Kurtosis**                  | {:.2f}                      |
    | **VaR 95%**                   | {:.4f}                      |
    | **CVaR 95%**                  | {:.4f}                      |
    | **Max Drawdown (%)**          | {:.2f}%                     |
    | **Peak Date**                 | {}                          |
    | **Valley Date**               | {}                          |
    | **Decline Lenght (days) **    | {}                          |
    | **Recovery Date**             | {}                          |
    | **Recovery Lenght(days)**     | {}                          |
    | **Total Lenght (days)**       | {}                          |
    """.format(
        metricas['Rendimiento Anual (%)'],
        metricas['Rendimiento Acumulado (%)'],
        metricas['Volatilidad Anual (%)'],
        metricas['Sharpe Ratio'],
        metricas['Sortino Ratio'],
        metricas['Sesgo'],
        metricas['Curtosis'],
        metricas['VaR 95%'],
        metricas['CVaR 95%'],
        metricas['Máximo Drawdown (%)'],
        metricas['Fecha Pico'],
        metricas['Fecha Valle'],
        metricas['Duración de la Caída (días)'],
        metricas['Fecha Recuperación'],
        metricas['Duración Recuperación (días)'],
        metricas['Duración Total (días)']
    ))

    fig = graficar_drawdown_portafolio(precios_portafolio, f"{portafolio_seleccionado} Drawdown")
    st.plotly_chart(fig)

else:
    sp500 = obtener_datos_acciones(['^GSPC'], start_date)
    sp500_retornos = sp500.pct_change().dropna()
    sp500_acumulado = (1 + sp500_retornos).cumprod() - 1

    fig_comparacion = go.Figure()

    colores = ["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"]
    for i, pesos in enumerate(pesos_list):
        precios_portafolio = (retornos * pesos).sum(axis=1)
        rendimiento_acumulado = (1 + precios_portafolio).cumprod() - 1

        fig_comparacion.add_trace(go.Scatter(
            x=rendimiento_acumulado.index,
            y=rendimiento_acumulado,
            mode='lines',
            name=nombres_portafolios[i],
            line=dict(color=colores[i % len(colores)])
        ))

    fig_comparacion.add_trace(go.Scatter(
        x=sp500_acumulado.index,
        y=sp500_acumulado['^GSPC'],
        mode='lines',
        name='S&P 500',
        line=dict(color='red')
    ))

    fig_comparacion.update_layout(
        title="Cumulative Returns Comparison",
        xaxis_title="Date",
        yaxis_title="Cumulative Returns",
        yaxis_tickformat=".0%"
    )
    fig_comparacion.update_layout(
    title="Cumulative Returns Against Benchmark",
    xaxis_title="Date",
    yaxis_title="Cumulative Returns",
    yaxis_tickformat=".0%",
    height=450,  # Aumenta la altura de la figura
    width=1200,   # Aumenta el ancho de la figura
    legend=dict(
        x=0.01,  # Posición horizontal de la leyenda
        y=1.1,  # Posición vertical de la leyenda
        xanchor="left",  # Ancla a la izquierda
        yanchor="top",   # Ancla en la parte superior
        itemwidth=20,    # Ajusta el ancho de los elementos (opcional)
        valign="middle", # Alineación vertical de los elementos dentro del cuadro
        borderwidth=1,   # Ancho del borde del cuadro de leyenda
        bordercolor="gray"  # Color del borde (opcional)
    )
    )
    st.plotly_chart(fig_comparacion)

