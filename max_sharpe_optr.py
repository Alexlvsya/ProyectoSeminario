import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from numpy import around
from matplotlib import cm
from numpy import *
from numpy.linalg import multi_dot
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go  # Correct import for plotly.graph_objects
import plotly.express as px  # Import for plotly.express
import matplotlib.pyplot as plt # Import for matplotlib, if needed
from datetime import date

# Ignore warnings
import warnings
warnings.filterwarnings('ignore')

#Etf´s que componen el portfolio
symbols = ['EMB', 'XLE', 'SPXL', 'EEM', 'SHV']

# Numero de activos del portfolio
numofasset = len(symbols)

# Numero de portfolios para optimizacion
numofportfolio = 10000

def download_data(tickers, start_date='2010-01-01', end_date='2020-12-31'):
    data = yf.download(tickers, start=start_date, end=end_date)
    return data['Close']

#precio de cierre diario de cada activo
df=download_data(symbols)

# Normalizar los datos
normalized_data = df['2010':] / df['2010':].iloc[0]

# calcular retornos de los ETFs
returns = df.pct_change().fillna(0)

#funcion que simula portfolios
def portfolio_simulation(returns):
    # Initialize the lists
    rets = []; vols = []; wts = []
    # simula 10,000 portfolios
    for i in range (numofportfolio):
        # Genera pesos aleatorios
        weights = random.random(numofasset)[:, newaxis]
        # la suma de los pesos debe ser igual a 1
        weights /= sum(weights)
        # Portfolio statistics
        rets.append(weights.T @ array(returns.mean() * 252)[:, newaxis])
        vols.append(sqrt(multi_dot([weights.T, returns.cov()*252, weights])))
        wts.append(weights.flatten())
    # Create a dataframe for analysis
    portdf = 100*pd.DataFrame({
        'port_rets': array(rets).flatten(),
        'port_vols': array(vols).flatten(),
        'weights': list(array(wts))
        })
    portdf['sharpe_ratio'] = portdf['port_rets'] / portdf['port_vols']
    return round(portdf,2)

# Create a dataframe for analysis
temp = portfolio_simulation(returns)

# Get the max sharpe portfolio stats
temp.iloc[temp.sharpe_ratio.idxmax()]

# Max sharpe ratio portfolio weights
msrpwts = temp['weights'][temp['sharpe_ratio'].idxmax()]

# Allocation to achieve max sharpe ratio portfolio
j = dict(zip(symbols, around(msrpwts,2)))

# Datos proporcionados
colors = ["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"]

# Separar los nombres y los valores
labels = list(j.keys())
sizes = list(j.values())

# Crear gráfica de pastel
plt.figure(figsize=(8, 8))
wedges, texts, autotexts = plt.pie(
    sizes,
    labels=labels,
    colors=colors,
    autopct='%1.1f%%',
    startangle=140,
    textprops={'fontsize': 12, 'weight': 'bold'},
    wedgeprops={'edgecolor': 'black', 'linewidth': 0.7}
)

# Ajustar colores y tamaño de los porcentajes
for autotext in autotexts:
    autotext.set_color("white")
    autotext.set_fontweight("bold")

# Título y fondo gris
plt.title("Asset Allocation - Max Sharpe Ratio ", fontsize=20, weight="bold")
plt.gca().set_facecolor("lightgray")
plt.gcf().patch.set_facecolor("gray")



# Configuración de la página
st.set_page_config(
    page_title="Portfolio Simulation",
    page_icon="📊",
    layout="wide"
)

# Título de la página
st.title("Monte Carlo Portfolio Simulation")
st.write("Visualización de asignación de activos y portafolios simulados.")

# Datos proporcionados (gráfica de pastel)
symbols = ['EMB', 'XLE', 'SPXL', 'EEM', 'SHV']
weights = [0.0001, 0.0272, 0.2326, 0.7372, 0.00028] 
colors = ["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"]

# Gráfica de pastel
st.header("Max Sharpe Ratio - Asset Allocation")
fig_pie, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    weights,
    labels=symbols,
    colors=colors,
    autopct='%1.1f%%',
    startangle=140,
    textprops={'fontsize': 12, 'weight': 'bold'},
    wedgeprops={'edgecolor': 'black', 'linewidth': 0.7}
)
for autotext in autotexts:
    autotext.set_color("white")
    autotext.set_fontweight("bold")
ax.set_title("Asset Allocation - Max Sharpe Ratio", fontsize=20, weight="bold")
ax.set_facecolor("lightgray")
fig_pie.patch.set_facecolor("gray")
st.pyplot(fig_pie)

# Datos proporcionados (gráfica de dispersión)
# DataFrame de ejemplo para ilustración; reemplázalo con `temp`
import pandas as pd
temp = portfolio_simulation(returns)

# Gráfica de dispersión
st.header("Monte Carlo Simulated Portfolio")
fig_scatter = px.scatter(
    temp, x='port_vols', y='port_rets', color='sharpe_ratio',
    color_continuous_scale='Blues',
    labels={'port_vols': 'Expected Volatility', 'port_rets': 'Expected Return', 'sharpe_ratio': 'Sharpe Ratio'},
    title="Monte Carlo Simulated Portfolio"
)
# Añadir estrella para el máximo Sharpe Ratio
fig_scatter.add_scatter(
    mode='markers',
    x=[temp.loc[temp['sharpe_ratio'].idxmax(), 'port_vols']],
    y=[temp.loc[temp['sharpe_ratio'].idxmax(), 'port_rets']],
    marker=dict(color='#6A0DAD', size=20, symbol='star'),
    name='Max Sharpe'
)
fig_scatter.update_layout(
    plot_bgcolor='rgb(40, 40, 40)',
    paper_bgcolor='rgb(95, 95, 95)',
    font=dict(family='Arial', size=14, color='white'),
    title_font=dict(size=24, color='white'),
    xaxis=dict(title='Expected Volatility', color='white'),
    yaxis=dict(title='Expected Return', color='white')
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Pie de página
st.markdown("---")
st.write("Creado por [Tu Nombre](#).")
