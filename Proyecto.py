import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Portfolio Management and Asset Allocation",
    page_icon="📈",
    layout="wide",
)

# Título principal
st.title("Portfolio Management and Asset Allocation")
st.write("Created for the Portfolio Management an Asset Allocation Course, UNAM")

# Opciones principales
options = [
    "ETF Individual Analysis",
    "Picking our ETFs",
    "Portfolio Optimization",
    "Portfolio Backtesting",
    "Black-Litterman Model",
]

# Selección de la opción principal
main_option = st.sidebar.selectbox("Select an Option", options)

# Lógica para cada opción principal
if main_option == "ETF Individual Analysis":
    st.subheader("ETF Individual Analysis")
    etf_options = ["Metrics and Var/CVaR Analysis", "Drawdown Analysis"]
    etf_selection = st.selectbox("Selecciona un análisis", etf_options)

    if etf_selection == "Metrics and Var/CVaR Analysis":
        st.markdown("[Ir a Metrics and Var/CVaR Analysis](https://proyectoseminario-axpnjhfam5z8gv2ma8ntnx.streamlit.app/)")
    elif etf_selection == "Drawdown Analysis":
        st.markdown("[Ir a Drawdown Analysis](https://proyectoseminario-hbvka56leot26ekvwynaig.streamlit.app/)")
#letsgooo
elif main_option == "Picking our ETFs":
    st.subheader("Information About the ETFs that conform the Portfolio")
     
    st.markdown(
        """
        For more detailed insights on the ETFs, visit the following [ETF Information Page]( https://proyectoseminario-agjfdpx3d5glae6bwrzvzd.streamlit.app/ ).
        """,
    unsafe_allow_html=True
    )
    

elif main_option == "Portfolio Optimization":
    st.subheader("Portfolio Optimization")
    optimization_options = [
        "Max Sharpe Ratio",
        "Minimum Volatility",
        "Minimum Volatility with a 10% Objective",
    ]
    optimization_selection = st.selectbox(
        "Selecciona una estrategia de optimización", optimization_options
    )

    if optimization_selection == "Max Sharpe Ratio":
        st.markdown("[Ir a Max Sharpe Ratio](https://proyectoseminario-qd55yqhnxnqj9omqsomtaj.streamlit.app/)")
    elif optimization_selection == "Minimum Volatility":
        st.markdown("[Ir a Minimum Volatility](https://proyectoseminario-agqznvx4oz8tx5wpgbecmk.streamlit.app/)")
    elif optimization_selection == "Minimum Volatility with a 10% Objective":
        st.markdown("[Ir a Minimum Volatility with a 10% Objective](https://proyectoseminario-yjtip7ly38s5ndspy8iurm.streamlit.app/)")

elif main_option == "Portfolio Backtesting":
    st.subheader("Portfolio Backtesting")
    st.markdown("[Ir a Portfolio Backtesting](https://proyectoseminario-aievfsagdffprfdywghdn2.streamlit.app/)")

elif main_option == "Black-Litterman Model":
    st.subheader("Black-Litterman Model")
    st.markdown("[Ir a Black-Litterman Model](https://proyectoseminario-hagckoosfjvgxkcjtxxfjq.streamlit.app/)")

# Pie de página
st.markdown("The different analysis shown are not an investment reccomendations and are just for educational purposes")
st.write("Credits: Alejandro Ramirez Camacho y Emilio Dominguez Valenzuela.")