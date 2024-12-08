import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de Streamlit
st.set_page_config(page_title="Portfolio Optimization", page_icon="📊", layout="wide")
st.title("Portfolio Optimization")
st.write("Visualización de los pesos del portafolio con objetivo de mínima varianza.")

# ---- Datos iniciales ----
etfs = ["EMB", "XLE", "SPXL", "EEM", "SHV"]
start_date = "2010-01-01"
end_date = "2023-12-31"

# Descargar datos
@st.cache
def download_data(etfs, start_date, end_date):
    data = yf.download(etfs, start=start_date, end=end_date)["Adj Close"]
    return data

data = download_data(etfs, start_date, end_date)
usd_mxn = yf.download("USDMXN=X", start=start_date, end=end_date)["Adj Close"]

# Asegurar fechas comunes
common_dates = data.index.intersection(usd_mxn.index)
data = data.loc[common_dates]
usd_mxn = usd_mxn.loc[common_dates]

# Ajustar precios a pesos mexicanos
data_mxn = data.mul(usd_mxn, axis=0)

# Calcular rendimientos
daily_returns_mxn = data_mxn.pct_change()
total_returns_mxn = (data_mxn.iloc[-1] / data_mxn.iloc[0]) - 1
std_devs_mxn = daily_returns_mxn.std()
correlation_matrix_mxn = daily_returns_mxn.corr()

# Matriz de covarianza y cálculo de pesos
S_mxn = np.diag(std_devs_mxn)
covariance_matrix_mxn = S_mxn @ correlation_matrix_mxn.to_numpy() @ S_mxn
# Verificar las dimensiones de los datos
st.write("Dimensiones de los datos iniciales:")
st.write(f"ETFs ajustados (MXN): {data_mxn.shape}")
st.write(f"Rendimientos diarios: {daily_returns_mxn.shape}")

# Recalcular la matriz de covarianza en pesos
covariance_matrix_mxn = daily_returns_mxn.cov().to_numpy()

# Ajustar dimensiones para total_returns_mxn
total_returns_mxn = total_returns_mxn.loc[data_mxn.columns]  # Asegúrate de alinear con las columnas de los ETFs

# Inversa de la matriz de covarianza
covariance_matrix_inv_mxn = np.linalg.inv(covariance_matrix_mxn)

# Recalcular A, B y C
ones = np.ones(len(etfs))  # Esto debe coincidir con el número de ETFs
A_mxn = ones @ covariance_matrix_inv_mxn @ ones
B_mxn = total_returns_mxn @ covariance_matrix_inv_mxn @ ones
C_mxn = total_returns_mxn @ covariance_matrix_inv_mxn @ total_returns_mxn




expected_return_mxn = 0.10 / 252  # Rendimiento objetivo diario ajustado
denominator_mxn = (A_mxn * C_mxn - B_mxn**2)
_lambda_mxn = (expected_return_mxn * A_mxn - B_mxn) / denominator_mxn
_gamma_mxn = (C_mxn - expected_return_mxn * B_mxn) / denominator_mxn

# Calcular los pesos del portafolio
_lambda_mxn = (expected_return_mxn * A_mxn - B_mxn) / denominator_mxn
_gamma_mxn = (C_mxn - expected_return_mxn * B_mxn) / denominator_mxn
weights_mxn = covariance_matrix_inv_mxn @ (_lambda_mxn * total_returns_mxn.to_numpy() + _gamma_mxn * ones)

# Crear DataFrame de pesos
weights_df_mxn = pd.DataFrame(weights_mxn, index=etfs, columns=["Pesos"])

weights_df_mxn = pd.DataFrame(weights_mxn, index=etfs, columns=["Pesos"])

# ---- Configuración para la gráfica ----
sns.set_theme(style="whitegrid", palette="deep")

fig, ax = plt.subplots(figsize=(12, 6))
weights_df_mxn_sorted = weights_df_mxn.sort_values(by="Pesos", ascending=False)

# Colores personalizados
colors = ["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"]
bar_colors = [colors[i % len(colors)] for i in range(len(weights_df_mxn))]

# Graficar barras
bars = ax.bar(
    weights_df_mxn_sorted.index,
    weights_df_mxn_sorted["Pesos"],
    color=bar_colors,
    edgecolor="black",
    linewidth=0.7,
)

# Etiquetas en las barras
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

# Configuración del gráfico
ax.set_title("Minimum Variance Portfolio Weights", fontsize=18, weight="bold")
ax.set_ylabel("Weight (%)", fontsize=14)
ax.set_xlabel("Assets", fontsize=14)
ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.grid(axis="y", linestyle="--", alpha=0.7)
ax.set_facecolor("lightgray")
fig.patch.set_facecolor("white")

# Mostrar gráfica en Streamlit
st.pyplot(fig)

# Mostrar tabla de pesos
st.subheader("Portfolio Weights")
st.dataframe(weights_df_mxn.style.format("{:.2%}"))
