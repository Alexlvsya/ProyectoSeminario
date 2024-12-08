from numpy import *
from numpy.linalg import multi_dot
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go  # Correct import for plotly.graph_objects
import plotly.express as px  # Import for plotly.express
import matplotlib.pyplot as plt # Import for matplotlib, if needed
from datetime import date
import seaborn as sns
import numpy as np
import streamlit as st

# Ignore warnings
import warnings
warnings.filterwarnings('ignore')


#Seccion Max Sharpe Ratio 


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

# Mostrar la gráfica
plt.tight_layout()
plt.show() #esta es la Gráfica de Pastel 

import plotly.express as px

# Plot simulated portfolio
fig = px.scatter(
    temp, x='port_vols', y='port_rets', color='sharpe_ratio',
    color_continuous_scale='Blues',  # Gradiente de color de rojo a verde
    labels={'port_vols': 'Expected Volatility', 'port_rets': 'Expected Return', 'sharpe_ratio': 'Sharpe Ratio'},
    title="Monte Carlo Simulated Portfolio"
).update_traces(
    mode='markers',
    marker=dict(symbol='cross', size=8)  # Elimina el contorno negro
)

# Plot max sharpe (estrella púrpura)
fig.add_scatter(
    mode='markers',
    x=[temp.iloc[temp.sharpe_ratio.idxmax()]['port_vols']],
    y=[temp.iloc[temp.sharpe_ratio.idxmax()]['port_rets']],
    marker=dict(color='#6A0DAD', size=20, symbol='star'),
    name='Max Sharpe'
).update(layout_showlegend=False)

# Mostrar spikes
fig.update_xaxes(showspikes=True)
fig.update_yaxes(showspikes=True)

# Personalizar el fondo del gráfico y la tipografía
fig.update_layout(
    plot_bgcolor='rgb(40, 40, 40)',  # Fondo gris oscuro
    paper_bgcolor='rgb(95, 95, 95)',  # Fondo de papel gris oscuro
    title_font=dict(family='Arial', size=24, color='white'),
    xaxis_title_font=dict(family='Arial', size=16, color='white'),
    yaxis_title_font=dict(family='Arial', size=16, color='white'),
    font=dict(family='Arial', size=14, color='white')  # Tipografía de todo el gráfico
)

fig.show() #esta es la gráfica de los 10000 portafolios simulados

#Seccion Minima Varianza 

# Import optimization module from scipy
import scipy.optimize as sco

# Define portfolio stats function
def portfolio_stats(weights):

    weights = array(weights)[:,newaxis]
    port_rets = weights.T @ array(returns.mean() * 252)[:,newaxis]
    port_vols = sqrt(multi_dot([weights.T, returns.cov() * 252, weights]))

    return array([port_rets, port_vols, port_rets/port_vols]).flatten()

# Maximizing sharpe ratio
def min_sharpe_ratio(weights):
    return -portfolio_stats(weights)[2]

# Each asset boundary ranges from 0 to 1
tuple((0, 1) for x in range(numofasset))

# Specify constraints and bounds
cons = ({'type': 'eq', 'fun': lambda x: sum(x) - 1})
bnds = tuple((0, 1) for x in range(numofasset))
initial_wts = numofasset*[1./numofasset]

# Optimizing for maximum sharpe ratio
opt_sharpe = sco.minimize(min_sharpe_ratio, initial_wts, method='SLSQP', bounds=bnds, constraints=cons)

# Portfolio weights
list(zip(symbols, around(opt_sharpe['x']*100,2)))

# Portfolio stats
stats = ['Returns', 'Volatility', 'Sharpe Ratio']
list(zip(stats, around(portfolio_stats(opt_sharpe['x']),4)))
# Minimize the variance
def min_variance(weights):
    return portfolio_stats(weights)[1]*2

# Optimizing for minimum variance
opt_var = sco.minimize(min_variance, initial_wts, method='SLSQP', bounds=bnds, constraints=cons)

# Portfolio weights
k = list(zip(symbols, around(opt_var['x']*100,2)))

# Datos proporcionados
k = [('EMB', 0.02), ('XLE', 0.0), ('SPXL', 99.91), ('EEM', 0.03), ('SHV', 0.04)]
colors = ["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"]

# Separar nombres de activos y pesos
activos, pesos = zip(*k)

# Configuración de la gráfica
plt.figure(figsize=(10, 6))
plt.bar(activos, pesos, color=colors, edgecolor="black", linewidth=0.7)

# Añadir etiquetas en las barras
for i, peso in enumerate(pesos):
    plt.text(i, peso + (0.5 if peso > 0 else -0.5),  # Posición de la etiqueta
             f"{peso:.2f}%", ha="center", va="bottom" if peso >= 0 else "top",
             fontsize=12, fontweight="bold", color="#2C3E50")

# Configuración del diseño
plt.title("Minimum Variance - Asset Allocation", fontsize=16, weight="bold")
plt.ylabel("Weight (%)", fontsize=14)
plt.xlabel("Assets", fontsize=14)
plt.axhline(0, color="black", linestyle="--", linewidth=0.8)  # Línea en el eje 0
plt.grid(axis="y", linestyle="--", alpha=0.6)

# Fondo gris para la figura
plt.gca().set_facecolor("lightgray")
plt.gcf().patch.set_facecolor("gray")

# Mostrar la gráfica
plt.tight_layout()
plt.show() #esta es la gráfica de Minima varianza 
# Portfolio stats
k = list(zip(stats, around(portfolio_stats(opt_var['x']),4)))
print(k)




#seccion Mínima Varianza con Objetivo del 10% en MXN 



# Definimos los ETFs y las fechas
etfs = ["EMB", "XLE", "SPXL", "EEM", "SHV"]
start_date = "2010-01-01"
end_date = "2023-12-31"

# Descargar datos de los ETFs
data = yf.download(etfs, start=start_date, end=end_date)["Adj Close"]

# Descargar datos del tipo de cambio USD/MXN
usd_mxn = yf.download("USDMXN=X", start=start_date, end=end_date)["Adj Close"]

# Asegurarnos de que solo usamos las fechas comunes entre los datos de ETFs y USD/MXN
common_dates = data.index.intersection(usd_mxn.index)

# Filtrar ambos conjuntos de datos para que solo contengan las fechas comunes
data = data.loc[common_dates]
usd_mxn = usd_mxn.loc[common_dates]

# Ajustar los precios de los ETFs a pesos mexicanos

usd_mxn = usd_mxn.rename(columns={"Adj Close": "USDMXN=X"})


# Multiplicamos cada columna de ETFs por la serie de tipo de cambio correspondiente
data_mxn = data.mul(usd_mxn["USDMXN=X"], axis=0)

# Calcular los rendimientos diarios en pesos
daily_returns_mxn = data_mxn.pct_change()

# Calcular el rendimiento total en pesos (rendimiento acumulado desde el inicio hasta el fin)
total_returns_mxn = (data_mxn.iloc[-1] / data_mxn.iloc[0]) - 1

# Calcular la desviación estándar de los rendimientos diarios en pesos
std_devs_mxn = daily_returns_mxn.std()

# Calcular la matriz de correlación en pesos
correlation_matrix_mxn = daily_returns_mxn.corr()

# Crear la matriz diagonal S a partir del vector de desviaciones estándar
S_mxn = np.diag(std_devs_mxn)

# Calcular la matriz de covarianza en pesos
covariance_matrix_mxn = S_mxn @ correlation_matrix_mxn.to_numpy() @ S_mxn

#inversa
covariance_matrix_inv_mxn = np.linalg.inv(covariance_matrix_mxn)

# Crear el vector de unos
ones = np.ones(len(etfs))

# Calcular A, B, y C en pesos
A_mxn = ones @ covariance_matrix_inv_mxn @ ones
B_mxn = total_returns_mxn @ covariance_matrix_inv_mxn @ ones
C_mxn = total_returns_mxn @ covariance_matrix_inv_mxn @ total_returns_mxn

# Parámetros para el portafolio
expected_return_mxn = 0.10 / 252  # Rendimiento objetivo diario ajustado (asumiendo 252 días hábiles)
denominator_mxn = (A_mxn * C_mxn - B_mxn**2)
_lambda_mxn = (expected_return_mxn * A_mxn - B_mxn) / denominator_mxn
_gamma_mxn = (C_mxn - expected_return_mxn * B_mxn) / denominator_mxn

# Calcular los pesos del portafolio en pesos
weights_mxn = covariance_matrix_inv_mxn @ (_lambda_mxn * total_returns_mxn + _gamma_mxn * ones)

# Opcional: Mostrar los pesos en un DataFrame para mejor legibilidad
weights_df_mxn = pd.DataFrame(weights_mxn, index=etfs, columns=["Pesos"])


# Configuración para la gráfica profesional
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["axes.titlesize"] = 16
plt.rcParams["axes.labelsize"] = 14
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
plt.rcParams["font.family"] = "sans-serif"

# Colores personalizados
colors = ["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"]

# Crear gráfica de barras
fig, ax = plt.subplots()

# Datos para la gráfica
weights_df_mxn_sorted = weights_df_mxn.sort_values(by="Pesos", ascending=False)
bar_colors = [colors[i % len(colors)] for i in range(len(weights_df_mxn))]

# Graficar barras
bars = ax.bar(
    weights_df_mxn_sorted.index,
    weights_df_mxn_sorted["Pesos"],
    color=bar_colors,
    edgecolor="black",
    linewidth=0.7,
)

# Añadir etiquetas en las barras
for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        height + (0.01 if height >= 0 else -0.02),
        f"{height:.2%}",
        ha="center",
        va="bottom" if height >= 0 else "top",
        fontsize=12,
        weight="bold",
        color="#2C3E50",
    )

# Configuración de ejes y títulos
ax.set_title("Minimum Variance with 10% Objective Portfolio Weights", fontsize=18, weight="bold")
ax.set_ylabel("Weight (%)", fontsize=14)
ax.set_xlabel("Assets", fontsize=14)
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")  # Línea en y=0 para resaltar negativos
ax.grid(axis="y", linestyle="--", alpha=0.7)

# Fondo de la gráfica
ax.set_facecolor("lightgray")
fig.patch.set_facecolor("white")

# Mostrar la gráfica
plt.tight_layout()
plt.show() #esta es la gráfica que devuelve el metodo de minima varianza con objetivo del 10 %

#streamlit

# Configure Streamlit page
st.set_page_config(
    page_title="Port Opt",
    layout="wide",
)

# Sidebar for optimization selection
st.sidebar.title("Select Optimization Method")
optimization_method = st.sidebar.radio(
    "Optimization Types:",
    ["Max Sharpe Ratio", "Minimum Variance", "Min Variance with 10% Objective"]
)

# Main section based on selection
if optimization_method == "Max Sharpe Ratio":
    st.title("Max Sharpe Ratio Portfolio Optimization")
    
    # Add first graph: Pie chart for asset allocation
    st.subheader("Asset Allocation - Max Sharpe Ratio")
    fig1, ax1 = plt.subplots(figsize=(8, 8))
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

    st.pyplot(fig1) #mostrar la gráfica de pastel 

    # Add second graph: Monte Carlo simulation scatter plot
    st.subheader("Monte Carlo Simulated Portfolio")
    # Replace with the relevant Plotly scatter plot code
    # (Paste the Plotly scatter plot code here, for brevity it's excluded)
    # Plot simulated portfolio
    fig = px.scatter(
    temp, x='port_vols', y='port_rets', color='sharpe_ratio',
    color_continuous_scale='Blues',  # Gradiente de color de rojo a verde
    labels={'port_vols': 'Expected Volatility', 'port_rets': 'Expected Return', 'sharpe_ratio': 'Sharpe Ratio'},
    title="Monte Carlo Simulated Portfolio"
    ).update_traces(
    mode='markers',
    marker=dict(symbol='cross', size=8)  # Elimina el contorno negro
    )

    # Plot max sharpe (estrella púrpura)
    fig.add_scatter(
    mode='markers',
    x=[temp.iloc[temp.sharpe_ratio.idxmax()]['port_vols']],
    y=[temp.iloc[temp.sharpe_ratio.idxmax()]['port_rets']],
    marker=dict(color='#6A0DAD', size=20, symbol='star'),
    name='Max Sharpe'
    ).update(layout_showlegend=False)

    # Mostrar spikes
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)

    # Personalizar el fondo del gráfico y la tipografía
    fig.update_layout(
    plot_bgcolor='rgb(40, 40, 40)',  # Fondo gris oscuro
    paper_bgcolor='rgb(95, 95, 95)',  # Fondo de papel gris oscuro
    title_font=dict(family='Arial', size=24, color='white'),
    xaxis_title_font=dict(family='Arial', size=16, color='white'),
    yaxis_title_font=dict(family='Arial', size=16, color='white'),
    font=dict(family='Arial', size=14, color='white')  # Tipografía de todo el gráfico
    )

    # Example placeholder for the scatter plot:
    st.plotly_chart(fig)

elif optimization_method == "Minimum Variance":
    st.title("Minimum Variance Portfolio Optimization")
    
    # Add bar chart for Minimum Variance
    st.subheader("Minimum Variance - Asset Allocation")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    # Replace with the relevant code or data for the bar chart
    plt.bar(activos, pesos, color=colors, edgecolor="black", linewidth=0.7)

    # Añadir etiquetas en las barras
    for i, peso in enumerate(pesos):
        plt.text(i, peso + (0.5 if peso > 0 else -0.5),  # Posición de la etiqueta
        f"{peso:.2f}%", ha="center", va="bottom" if peso >= 0 else "top",
        fontsize=12, fontweight="bold", color="#2C3E50")

    # Configuración del diseño
    plt.title("Minimum Variance - Asset Allocation", fontsize=16, weight="bold")
    plt.ylabel("Weight (%)", fontsize=14)
    plt.xlabel("Assets", fontsize=14)
    plt.axhline(0, color="black", linestyle="--", linewidth=0.8)  # Línea en el eje 0
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    # Fondo gris para la figura
    plt.gca().set_facecolor("lightgray")
    plt.gcf().patch.set_facecolor("gray")

    st.pyplot(fig2)

elif optimization_method == "Min Variance with 10% Objective":
    st.title("Minimum Variance with 10% Objective Portfolio Optimization")
    
    # Add bar chart for Min Variance with 10% Objective
    st.subheader("Minimum Variance with 10% Objective - Asset Allocation")
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    # Replace with the relevant code or data for the bar chart
    weights_df_mxn_sorted = weights_df_mxn.sort_values(by="Pesos", ascending=False)
    bar_colors = [colors[i % len(colors)] for i in range(len(weights_df_mxn))]

    # Graficar barras
    bars = ax.bar(
    weights_df_mxn_sorted.index,
    weights_df_mxn_sorted["Pesos"],
    color=bar_colors,
    edgecolor="black",
    linewidth=0.7,
    )

    # Añadir etiquetas en las barras
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + (0.01 if height >= 0 else -0.02),
            f"{height:.2%}",
            ha="center",
            va="bottom" if height >= 0 else "top",
            fontsize=12,
            weight="bold",
            color="#2C3E50",
        )

    # Configuración de ejes y títulos
    ax.set_title("Minimum Variance with 10% Objective Portfolio Weights", fontsize=18, weight="bold")
    ax.set_ylabel("Weight (%)", fontsize=14)
    ax.set_xlabel("Assets", fontsize=14)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")  # Línea en y=0 para resaltar negativos
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Fondo de la gráfica
    ax.set_facecolor("lightgray")
    fig.patch.set_facecolor("white")

    # (Paste the 10% Objective bar chart code here)
    st.pyplot(fig3)