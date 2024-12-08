import streamlit as st

# Configuración inicial de la página de Streamlit
st.set_page_config(
    page_title="Portfolio of Minimum Variance and a 10% Objective (MXN) ",
    layout="wide",  # Página amplia para aprovechar más espacio
    initial_sidebar_state="expanded"
)

# Diseño profesional: Encabezado principal
st.markdown(
    """
    <style>
    .title-style {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 20px;
    }
    .subtitle-style {
        font-size: 1.2rem;
        color: #7F8C8D;
        text-align: center;
        margin-bottom: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title-style">Portfolio Allocation</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle-style">This Portfolio Allocation was calculated with the Minimum Variance Model and has a 10% Objective (MXN)</div>',
    unsafe_allow_html=True
)

# URL de la imagen en el repositorio de GitHub
image_url = "https://raw.githubusercontent.com/Alexlvsya/ProyectoSeminario/main/min10.png"

# Mostrar la imagen centrada con un mayor tamaño
st.markdown(
    f"""
    <div style="display: flex; justify-content: center; align-items: center; margin-top: 20px;">
        <img src="{image_url}" alt="Portfolio Visualization" style="width: 80%; border-radius: 10px; border: 2px solid #34495E;">
    </div>
    """,
    unsafe_allow_html=True
)
st.write('''The model shows an explicit preference for the SPXL (the SPXL has the Minimum variance in the 
         individual analysis of each ETF), followed by the EMB etf, the main and most interesting thing that 
         differenciate this model from the others is that this allocation is sub-invested in the EEM etf, we 
         think its because of the high volatility and small returns on the time period. ''')
# Pie de página profesional
st.markdown(
    """
    <style>
    .footer-style {
        font-size: 0.9rem;
        color: #BDC3C7;
        text-align: center;
        margin-top: 40px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="footer-style">Credits Alejandro Ramirez Camacho Emilio Dominguez Valenzuela</div>', unsafe_allow_html=True)
