import plotly.express as px
import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pypfopt import EfficientFrontier, objective_functions
from pypfopt import black_litterman, risk_models
from pypfopt import BlackLittermanModel, plotting
from pypfopt import DiscreteAllocation

# creamos el portafolio
symbols_bl = ['EMB', 'XLE', 'SPXl', 'EEM', 'SHV']

#descargamos los datos de las acciones
start_date = "2010-01-01"
data_bl = yf.download(symbols_bl, start=start_date)["Adj Close"]

market_prices = yf.download("SPY", start=start_date)["Adj Close"]

#obtenemos marketcaps aproximadas
def obtener_marketcap(symbols):
    capitalizaciones = {}
    for symbol in symbols:
        try:
            # Obtener datos del símbolo
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Obtener precio de cierre más reciente
            precio_cierre = ticker.history(period="1d").iloc[-1]['Close']

            # Obtener totalAssets
            total_activos = info.get("totalAssets", None)

            if precio_cierre is not None and total_activos is not None:
                capitalizacion_aproximada = precio_cierre * total_activos
                capitalizaciones[symbol] = capitalizacion_aproximada
            else:
                capitalizaciones[symbol] = "Datos insuficientes"
        except Exception as e:
            capitalizaciones[symbol] = f"Error: {e}"
    return capitalizaciones

# Llamada a la función
capitalizacion = obtener_marketcap(symbols_bl)



#Convert capitalizacion to a Pandas Series
capitalizacion = pd.Series(capitalizacion)

#Reindex capitalizacion to match the covariance matrix
capitalizacion = capitalizacion.reindex(data_bl.columns)

# Ensure all values in 'capitalizacion' are numeric
capitalizacion = pd.to_numeric(capitalizacion, errors='coerce').fillna(0)

#obtenemos los priors
S = risk_models.CovarianceShrinkage(data_bl).ledoit_wolf()
delta = black_litterman.market_implied_risk_aversion(market_prices)
#lets gooooooo
# Check for NaN values in the covariance matrix
if S.isnull().values.any():
    print("Warning: Covariance matrix contains NaN values.")
    # Handle NaN values in S (e.g., using fillna or dropna)

# Check if the index is truly aligned
if not S.index.equals(capitalizacion.index):
    print("Warning: Index of covariance matrix and market caps do not match.")
    # Reindex or align the index further

plt.figure(figsize=(7, 5))
sns.heatmap(S.corr(), cmap='coolwarm', annot=True, fmt=".2f", cbar_kws={'shrink': 0.8})

# Personalizar el fondo
plt.gcf().set_facecolor('#2C3E50')  # Fondo gris oscuro

# Añadir la leyenda personalizada en la esquina inferior derecha
plt.figtext(
    0.95,
    0.02,
    "ARC Investing",
    horizontalalignment="right",
    fontsize=12,
    weight="bold",
    fontstyle="italic",
    color="#FFFFFF",
    family="serif"
)

# Mostrar el gráfico
plt.tight_layout()
plt.show()

market_prior = black_litterman.market_implied_prior_returns(capitalizacion, delta, S)

#MARKET PRIOR RETURNS

# Simulación del DataFrame market_prior
market_prior_data = {
    "Market Prior Returns": [0.115178, 0.035586, 0.000486, 0.282617, 0.198647]
}
market_prior = pd.DataFrame(market_prior_data, index=["EEM", "EMB", "SHV", "SPXL", "XLE"])

# Colores personalizados
colors = ["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"]

# Crear el gráfico de barras horizontales
fig, ax = plt.subplots(figsize=(10, 5))
market_prior.plot.barh(ax=ax, color=colors, width=0.8)

# Personalización del gráfico
ax.set_facecolor("#D3D3D3")  # Fondo gris
ax.set_title("Market Prior Returns", fontsize=16, weight="bold", color="#2C3E50", pad=20)
ax.set_xlabel("Returns", fontsize=14, color="#2C3E50")
ax.set_ylabel("ETFs", fontsize=14, color="#2C3E50")
ax.tick_params(axis="x", labelsize=12, color="#2C3E50")
ax.tick_params(axis="y", labelsize=12, color="#2C3E50")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#2C3E50")
ax.spines["bottom"].set_color("#2C3E50")



# Ajuste de posición de los textos
ax.set_xlim(left=0)  # Asegura que las barras no se corten

# Texto personalizado al pie del gráfico (esquina inferior derecha)
plt.figtext(
    0.95,
    0.02,
    "ARC Investing",
    horizontalalignment="right",
    fontsize=12,
    weight="bold",
    fontstyle="italic",
    color="#2C3E50",
    family="serif",
)

plt.tight_layout()
plt.show()
#expected 1y returns according to our views
views = {
    'EMB': 0.01,
    'XLE': 0.15,
    'SPXL':0.55,
    'EEM': 0.10,
    'SHV': 0.02,

  }

bl = BlackLittermanModel(S, pi=market_prior, absolute_views=views)

#intervalos de confianza
intervals = [ (0.1,0.35),
             (0.35,0.65),
              (0.5,0.8),
              (0.2,0.5),
              (0.2,0.4)
          ]
variances = []
for lb, ub in intervals:
    sigma = (ub - lb)/2
    variances.append(sigma ** 2)


omega = np.diag(variances)
#atajo para calcular automaticamente el market-implied prior
bl = BlackLittermanModel(S,pi="market", market_caps = capitalizacion, risk_aversion=delta, absolute_views=views, omega=omega)

#Posterior of estimate returns
ret_bl = bl.bl_returns()

rets_df = pd.DataFrame({
    "Prior": market_prior.values.flatten(),
    "Posterior": ret_bl.values.flatten(),
    "Views": pd.Series(views)
}).T
# Simulación del DataFrame rets_df
data = {
    "prior": [0.115178, 0.035586, 0.000486, 0.282617, 0.198647],
    "posterior": [0.139713, 0.042008, 0.000513, 0.364770, 0.221854],
    "views": [0.1, 0.01, 0.02, 0.55, 0.15],
}
rets_df = pd.DataFrame(data, index=["EEM", "EMB", "SHV", "SPXL", "XLE"])

# Colores preferidos
colors = ["#2C3E50", "#1ABC9C", "#6A5ACD"]

# Crear el gráfico de barras
fig, ax = plt.subplots(figsize=(12, 8))
rets_df.plot.bar(ax=ax, color=colors, width=0.8)

# Personalización del gráfico
ax.set_facecolor("#D3D3D3")  # Fondo gris
ax.set_title("Returns Comparison", fontsize=16, weight="bold", color="#2C3E50")
ax.set_ylabel("Returns", fontsize=14, color="#2C3E50")
ax.set_xlabel("ETFs", fontsize=14, color="#2C3E50")
ax.tick_params(axis="x", labelsize=12, color="#2C3E50")
ax.tick_params(axis="y", labelsize=12, color="#2C3E50")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#2C3E50")
ax.spines["bottom"].set_color("#2C3E50")

# Leyenda personalizada
ax.legend(
    title="Metrics",
    title_fontsize=12,
    fontsize=10,
    loc="upper left",
    frameon=False,
    labels=["Prior", "Posterior", "Views"],
)

# Texto personalizado al pie del gráfico
plt.figtext(
    0.5,
    0.02,
    "ARC Investing",
    horizontalalignment="right",
    fontsize=12,
    weight="bold",
    fontstyle="italic",
    color="#2C3E50",
    family="serif",
)

plt.tight_layout()
plt.show()

S_bl= bl.bl_cov()

#Max sharpe portfolio
ef = EfficientFrontier(ret_bl, S_bl)
ef.add_objective(objective_functions.L2_reg)
ef.max_sharpe()
weights = ef.clean_weights()
ef.portfolio_performance(verbose = True, risk_free_rate = 0.016)
#PORTFOLIO ALLOCATION USING BL MODEL
import matplotlib.pyplot as plt

# Datos de pesos (ejemplo con el OrderedDict que proporcionaste)
weights = {"EEM": 0.17947, "EMB": 0.05557, "SHV": 0.00093, "SPXL": 0.45799, "XLE": 0.30603}

# Colores preferidos
colors = ["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"]

# Crear el gráfico de pastel
fig, ax = plt.subplots(figsize=(7, 7))
fig.patch.set_facecolor("#D3D3D3")  # Fondo gris claro

wedges, texts, autotexts = ax.pie(
    weights.values(),
    labels=weights.keys(),
    autopct=lambda pct: f"{pct:.2f}%",
    colors=colors,
    startangle=90,
    textprops={"fontsize": 12},
)

# Estilizar el texto del gráfico
for autotext in autotexts:
    autotext.set_color("white")
    autotext.set_fontsize(10)
for text in texts:
    text.set_fontsize(12)

# Título
ax.set_title("Asset Allocation", fontsize=16, weight="bold")

# Texto personalizado centrado abajo
plt.figtext(
    0.5, 0.02,  # Posición centrada en la parte inferior
    "ARC Investing",
    horizontalalignment="center",
    fontsize=12,
    weight="bold",
    fontstyle="italic",
    color="#2C3E50",
    family="serif",
)

plt.show()

#interpretacion
view_emb=''' EMB: Para el Emerging Markets Bond, dada la reciente incertidumbre
 politica generada por las elecciones en USA, creemos que la inflacion en estos paises 
 se puede disparar debido a un aumento en los precios de los commodities,
  nuestro view a un año es de un avance del 1%, sin embargo, las bajadas de tasas a 
  nivel mundial nos llevan a colocar un  intervalo de confiaza 
  que va de 10% a un 35%'''
view_xle='''XLE: '''
view_spxl='''SPXL: '''
view_eem='''EEM: '''
view_shv='''SHV: '''

# Configuración de la página
title = "Portfolio Optimization using Black-Litterman´s Model"
st.set_page_config(page_title=title, layout="wide")
st.title(title)

# Opciones para la selección
graph_options = [
    "Correlation Heatmap",
    "Market Prior Returns",
    "Returns Comparison",
    "Portfolio Weights",
    "All Views"
]

# Simulaciones de datos y gráficos para demostración
def plot_correlation_heatmap():
    S_corr = np.random.rand(5, 5)  # Matriz de correlación simulada
    np.fill_diagonal(S_corr, 1)
    df_corr = pd.DataFrame(S_corr, columns=["EEM", "EMB", "SHV", "SPXL", "XLE"], index=["EEM", "EMB", "SHV", "SPXL", "XLE"])
    plt.figure(figsize=(6, 4))
    sns.heatmap(df_corr, annot=True, cmap="coolwarm", cbar_kws={'shrink': 0.8})
    st.pyplot(plt)

def plot_market_prior_returns():
    market_prior_data = {
        "Market Prior Returns": [0.115, 0.036, 0.0005, 0.283, 0.199]
    }
    df = pd.DataFrame(market_prior_data, index=["EEM", "EMB", "SHV", "SPXL", "XLE"])
    df.plot.barh(color=["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"], figsize=(10, 5))
    plt.title("Market Prior Returns", fontsize=16)
    plt.tight_layout()
    st.pyplot(plt)

def plot_returns_comparison():
    data = {
        "Prior": [0.115, 0.036, 0.0005, 0.283, 0.199],
        "Posterior": [0.14, 0.042, 0.0005, 0.365, 0.222],
        "Views": [0.1, 0.01, 0.02, 0.55, 0.15]
    }
    df = pd.DataFrame(data, index=["EEM", "EMB", "SHV", "SPXL", "XLE"])
    df.plot.bar(figsize=(10, 6), color=["#2C3E50", "#1ABC9C", "#6A5ACD"])
    plt.title("Returns Comparison", fontsize=16)
    plt.tight_layout()
    st.pyplot(plt)

def plot_portfolio_weights():
    weights = {"EEM": 0.18, "EMB": 0.06, "SHV": 0.001, "SPXL": 0.46, "XLE": 0.3}
    plt.figure(figsize=(7, 7))
    plt.pie(weights.values(), labels=weights.keys(), autopct='%1.1f%%', startangle=90, colors=["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"])
    plt.title("Portfolio Weights", fontsize=16)
    st.pyplot(plt)

def show_views():
    st.subheader("Views")
    views = {
        "EMB": "EMB: Para el Emerging Markets Bond, dada la reciente incertidumbre política generada por las elecciones en USA, creemos que la inflación en estos países se puede disparar debido a un aumento en los precios de los commodities.",
        "XLE": "XLE: Sector energético con buenas perspectivas a corto plazo debido al aumento en la demanda global de energía.",
        "SPXL": "SPXL: ETF apalancado con un rendimiento proyectado del 55% a 1 año según nuestras predicciones.",
        "EEM": "EEM: Mercados emergentes con un retorno esperado del 10% influenciado por la recuperación económica global.",
        "SHV": "SHV: Baja volatilidad con retornos proyectados de 2%."
    }
    for asset, view in views.items():
        st.markdown(f"**{asset}**: {view}")

# Selector de gráficos y vistas
selected_option = st.sidebar.selectbox("Choose what to display:", graph_options)

if selected_option == "Correlation Heatmap":
    st.subheader("Correlation Heatmap")
    plot_correlation_heatmap()
    st.subheader("Analysis")
    st.write('''In this chart are displayed all correlations between the different
             assets that will conform the portfolio. There are some highlights here that 
             we would like to remark; as expected , correlation between SHV and the other ETFS 
             is quite low (negative at every ETF); the maximum correlation between assets is achieved 
             by the SPXL and the EEM (98), actually, all correlations (not SHV case) are very high
             with values over .85.  ''')
elif selected_option == "Market Prior Returns":
    st.subheader("Market Prior Returns")
    plot_market_prior_returns()
elif selected_option == "Returns Comparison":
    st.subheader("Returns Comparison")
    plot_returns_comparison()
elif selected_option == "Portfolio Weights":
    st.subheader("Portfolio Weights")
    plot_portfolio_weights()
elif selected_option == "All Views":
    show_views()
#prueba sync git 