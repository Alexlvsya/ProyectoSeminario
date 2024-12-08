import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from numpy import *
from numpy.linalg import multi_dot
import pandas as pd
import yfinance as yf
from datetime import date
import warnings

# Ignorar advertencias
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(page_title="Portfolio Simulations", page_icon="📈", layout="wide")

# Título de la aplicación
st.title("Portfolio Simulations")
st.write("Visualización de portafolios simulados y asignación de activos con el máximo Sharpe Ratio.")

# Datos iniciales
symbols = ['EMB', 'XLE', 'SPXL', 'EEM', 'SHV']
numofasset = len(symbols)
numofportfolio = 10000

# Función para descargar datos
@st.cache
def download_data(tickers, start_date='2010-01-01', end_date='2020-12-31'):
    data = yf.download(tickers, start=start_date, end=end_date)
    return data['Close']

# Descargar datos
df = download_data(symbols)

# Normalizar los datos
normalized_data = df['2010':] / df['2010':].iloc[0]

# Calcular retornos de los ETFs
returns = df.pct_change().fillna(0)

# Función para simular portafolios
def portfolio_simulation(returns):
    rets, vols, wts = [], [], []
    for i in range(numofportfolio):
        weights = random.random(numofasset)[:, newaxis]
        weights /= sum(weights)
        rets.append(weights.T @ array(returns.mean() * 252)[:, newaxis])
        vols.append(sqrt(multi_dot([weights.T, returns.cov() * 252, weights])))
        wts.append(weights.flatten())
    portdf = 100 * pd.DataFrame({
        'port_rets': array(rets).flatten(),
        'port_vols': array(vols).flatten(),
        'weights': list(array(wts))
    })
    portdf['sharpe_ratio'] = portdf['port_rets'] / portdf['port_vols']
    return round(portdf, 2)

# Simular portafolios
temp = portfolio_simulation(returns)

# Obtener el portafolio de máximo Sharpe Ratio
max_sharpe_port = temp.iloc[temp.sharpe_ratio.idxmax()]
msrpwts = max_sharpe_port['weights']

# Asignación de activos para el máximo Sharpe Ratio
allocation = dict(zip(symbols, around(msrpwts, 2)))

# Colores para la gráfica
colors = ["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"]

# ---- Gráfica de pastel ----
st.subheader("Asset Allocation - Max Sharpe Ratio")

fig_pie, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    list(allocation.values()),
    labels=list(allocation.keys()),
    colors=colors,
    autopct='%1.1f%%',
    startangle=140,
    textprops={'fontsize': 12, 'weight': 'bold'},
    wedgeprops={'edgecolor': 'black', 'linewidth': 0.7}
)

# Ajustar colores de porcentajes
for autotext in autotexts:
    autotext.set_color("white")
    autotext.set_fontweight("bold")

ax.set_title("Asset Allocation - Max Sharpe Ratio", fontsize=20, weight="bold")
ax.set_facecolor("lightgray")
fig_pie.patch.set_facecolor("gray")

st.pyplot(fig_pie)

# ---- Gráfica de portafolios simulados ----
st.subheader("Monte Carlo Simulated Portfolio")

fig_scatter = px.scatter(
    temp,
    x='port_vols',
    y='port_rets',
    color='sharpe_ratio',
    color_continuous_scale='Blues',
    labels={'port_vols': 'Expected Volatility', 'port_rets': 'Expected Return', 'sharpe_ratio': 'Sharpe Ratio'},
    title="Monte Carlo Simulated Portfolio"
)

# Añadir el portafolio de máximo Sharpe Ratio como estrella
fig_scatter.add_scatter(
    mode='markers',
    x=[max_sharpe_port['port_vols']],
    y=[max_sharpe_port['port_rets']],
    marker=dict(color='#6A0DAD', size=20, symbol='star'),
    name='Max Sharpe'
)

# Personalizar el diseño
fig_scatter.update_layout(
    plot_bgcolor='rgb(40, 40, 40)',
    paper_bgcolor='rgb(95, 95, 95)',
    font=dict(family='Arial', size=14, color='white'),
    title_font=dict(family='Arial', size=24, color='white'),
    xaxis_title_font=dict(family='Arial', size=16, color='white'),
    yaxis_title_font=dict(family='Arial', size=16, color='white')
)

st.plotly_chart(fig_scatter, use_container_width=True)

# Pie de página
st.markdown("---")
st.write("Creado por [Tu Nombre](#).")

