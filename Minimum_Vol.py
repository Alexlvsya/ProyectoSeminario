import streamlit as st 
import matplotlib.pyplot as plt
from numpy import around

# Datos proporcionados
k = [('EMB', 0.02), ('XLE', 0.0), ('SPXL', 99.91), ('EEM', 0.03), ('SHV', 0.04)]
colors = ["#2C3E50", "#1ABC9C", "#6A5ACD", "#4682B4", "#708090"]

stats = ['Returns', 'Volatility', 'Sharpe Ratio']
portfolio_stats_values = [0.04, 0.34, 0.1198]  # Valores de ejemplo; reemplaza con `portfolio_stats(opt_var['x'])` en tu implementación.

# Configuración de la página
st.set_page_config(
    page_title="Minimum Variance Portfolio",
    page_icon="📊",
    layout="wide"
)

# Título de la página
st.title("Minimum Volatility Portfolio")
st.write("The following allocation was calculated with the Minimum Variance Portafolio method.")

# Sección de visualización
st.header("Asset Allocation")

# Separar nombres de activos y pesos
activos, pesos = zip(*k)

# Crear gráfica en Matplotlib
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(activos, pesos, color=colors, edgecolor="black", linewidth=0.7)

# Añadir etiquetas en las barras
for i, peso in enumerate(pesos):
    ax.text(i, peso + (0.5 if peso > 0 else -0.5),
            f"{peso:.2f}%", ha="center", va="bottom" if peso >= 0 else "top",
            fontsize=12, fontweight="bold", color="#2C3E50")

# Configuración del diseño
ax.set_title("Minimum Variance - Asset Allocation", fontsize=16, weight="bold")
ax.set_ylabel("Weight (%)", fontsize=14)
ax.set_xlabel("Assets", fontsize=14)
ax.axhline(0, color="black", linestyle="--", linewidth=0.8)
ax.grid(axis="y", linestyle="--", alpha=0.6)

# Fondo gris para la figura
ax.set_facecolor("lightgray")
fig.patch.set_facecolor("gray")

# Mostrar gráfica en Streamlit
st.pyplot(fig)

# Sección de estadísticas del portafolio
st.header("Portfolio Satistics")
stats_table = list(zip(stats, around(portfolio_stats_values, 4)))

# Mostrar estadísticas en tabla
st.table(stats_table)
st.write('''If we go back to the ETF stats, que will notice that the SPXL is the ETF with the 
         minimum volatility, so in this case, the optimization is giving 
         us a corner solution, allocating almost all of the portfolio 
         value in just one ETF, the one that has the Minimum Volatility ''')
# Pie de página
st.markdown("This is not an investment Recommendation ")
st.write("Credits: Alejandro Ramírez Camacho and Emilio Dominguez Valenzuela.")
