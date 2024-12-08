import streamlit as st

# Configuración inicial de la página de Streamlit
st.set_page_config(
    page_title="Portfolio",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Título de la página
st.title("Portfolio")

# URL de la imagen en el repositorio de GitHub
image_url = "https://raw.githubusercontent.com/<Alexlvsya>/<ProyectoSeminario>/<main>/min10.png"

# Mostrar la imagen en Streamlit
st.image(image_url, caption="Portfolio Visualization", use_column_width=True)

