import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Portfolio Management and Asset Allocation",
    page_icon="📈",
    layout="wide",
)

# Sección específica para probar el enlace
st.subheader("Information About the ETFs that conform the Portfolio")
st.markdown(
    """
    For more detailed insights on the ETFs, visit the following [ETF Information Page](https://proyectoseminario-agjfdpx3d5glae6bwrzvzd.streamlit.app/).
    """,
    unsafe_allow_html=True
)