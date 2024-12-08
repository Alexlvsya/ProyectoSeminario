import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Configuración inicial de la página de Streamlit
st.set_page_config(
    page_title="Portfolio Weights Visualization",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("Minimum Variance Portfolio Weights")
st.markdown(
    """
    ### Una herramienta interactiva para visualizar los pesos del portafolio objetivo
    Este análisis se basa en un portafolio mínimo de varianza ajustado al tipo de cambio USD/MXN.
    """
)

# Sidebar para parámetros
st.sidebar.header("Parámetros de entrada")
etfs = st.sidebar.multiselect(
    "Selecciona los ETFs:",
    options=["EMB", "XLE", "SPXL", "EEM", "SHV"],
    default=["EMB", "XLE", "SPXL", "EEM", "SHV"]
)
start_date = st.sidebar.date_input("Fecha de inicio:", value=pd.to_datetime("2010-01-01"))
end_date = st.sidebar.date_input("Fecha de fin:", value=pd.to_datetime("2023-12-31"))

# Validación de fechas
if start_date >= end_date:
    st.sidebar.error("La fecha de inicio debe ser anterior a la fecha de fin.")
else:
    # Descargar datos de ETFs y tipo de cambio USD/MXN
    data = yf.download(etfs, start=start_date, end=end_date)["Adj Close"]
    usd_mxn = yf.download("USDMXN=X", start=start_date, end=end_date)["Adj Close"]

    # Procesamiento de datos
    common_dates = data.index.intersection(usd_mxn.index)
    data = data.loc[common_dates]
    usd_mxn = usd_mxn.loc[common_dates]
    data_mxn = data.mul(usd_mxn, axis=0)

    # Calcular rendimientos diarios y estadísticas
    daily_returns_mxn = data_mxn.pct_change()
    total_returns_mxn = (data_mxn.iloc[-1] / data_mxn.iloc[0]) - 1
    std_devs_mxn = daily_returns_mxn.std()
    correlation_matrix_mxn = daily_returns_mxn.corr()

    # Matriz de covarianza
    S_mxn = np.diag(std_devs_mxn)
    covariance_matrix_mxn = S_mxn @ correlation_matrix_mxn.to_numpy() @ S_mxn
    covariance_matrix_inv_mxn = np.linalg.inv(covariance_matrix_mxn)

try:
    # Vector de unos ajustado a la cantidad de ETFs seleccionados
    ones = np.ones(len(etfs))

    # Cálculos de A, B y C
    A_mxn = ones @ covariance_matrix_inv_mxn @ ones
    B_mxn = total_returns_mxn @ covariance_matrix_inv_mxn @ ones
    C_mxn = total_returns_mxn @ covariance_matrix_inv_mxn @ total_returns_mxn

    # Parámetros del portafolio
    expected_return_mxn = 0.10 / 252
    denominator_mxn = (A_mxn * C_mxn - B_mxn**2)
    _lambda_mxn = (expected_return_mxn * A_mxn - B_mxn) / denominator_mxn
    _gamma_mxn = (C_mxn - expected_return_mxn * B_mxn) / denominator_mxn

    # Pesos del portafolio
    weights_mxn = covariance_matrix_inv_mxn @ (_lambda_mxn * total_returns_mxn + _gamma_mxn * ones)
    weights_df_mxn = pd.DataFrame(weights_mxn, index=etfs, columns=["Pesos"])

    # Mostrar resultados y gráfica
    st.subheader("Pesos calculados del portafolio")
    st.dataframe(weights_df_mxn.style.format({"Pesos": "{:.2%}"}))

    # Crear la gráfica (este bloque ya lo tienes implementado)
    ...



    # Visualización de los resultados
    st.subheader("Pesos calculados del portafolio")
    st.dataframe(weights_df_mxn.style.format({"Pesos": "{:.2%}"}))

    # Configuración de estilo y colores para la gráfica
    sns.set_theme(style="whitegrid", palette="deep")
    plt.rcParams["figure.figsize"] = (12, 6)
    plt.rcParams["axes.titlesize"] = 16
    plt.rcParams["axes.labelsize"] = 14
    colors = ["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"]

    # Crear la gráfica
    fig, ax = plt.subplots()
    weights_df_mxn_sorted = weights_df_mxn.sort_values(by="Pesos", ascending=False)
    bar_colors = [colors[i % len(colors)] for i in range(len(weights_df_mxn))]
    bars = ax.bar(
        weights_df_mxn_sorted.index,
        weights_df_mxn_sorted["Pesos"],
        color=bar_colors,
        edgecolor="black",
        linewidth=0.7
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
            color="#2C3E50"
        )

    # Configuración de ejes y títulos
    ax.set_title("Minimum Variance with 10% Objective Portfolio Weights", fontsize=18, weight="bold")
    ax.set_ylabel("Weight (%)", fontsize=14)
    ax.set_xlabel("Assets", fontsize=14)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_facecolor("lightgray")
    fig.patch.set_facecolor("white")

    # Mostrar la gráfica en Streamlit
    st.pyplot(fig)

except ValueError as e:
    st.error(f"Error al calcular el portafolio: {e}")