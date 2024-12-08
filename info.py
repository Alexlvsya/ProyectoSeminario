import streamlit as st

# Dictionary to store ETF information
def get_etf_info():
    return {
        "EMB": {
            "title": "(EMB) iShares J.P. Morgan USD Emerging Markets Bond",
            "category": "Emerging Markets Fixed Income",
            "exposure": "Provides exposure to bonds of varying maturities across multiple emerging market countries, holding a total of 632 positions.",
            "key_contributors": "Turkey (4.24%), Saudi Arabia (3.58%), Brazil (3.48%), Dominican Republic (3.27%), Philippines (3.26%), Colombia (3.25%), Mexico (3.15%)",
            "currency": "USD",
            "countries": "Asia, Africa, Latin America, and Eastern Europe",
            "risk_metrics": "Duration: 7.04, Convexity: 0.87, 3-year Beta: 0.57",
            "underlying_index": "JPMorgan EMBI Global Core Index",
            "ratings": "MSCI ESG: BB, Morningstar: 3 stars, Bronze medal",
            "cost": "$91.88",
            "fees": "0.39%",
            "managing_company": "BlackRock iShares J.P. Morgan",
            "political_outlook": "Protectionist U.S. policies may discourage production in emerging markets.",
            "economic_outlook": "Weakened currencies and rate increases may challenge economies and impact valuations."
        },
        "SPXL": {
            "title": "(SPXL) Direxion Daily S&P 500 Bull 3X Shares",
            "category": "Developed Markets Equity",
            "exposure": "3x leveraged exposure to the performance of the S&P 500.",
            "key_contributors": "Apple (7.30%), Microsoft (6.57%), Nvidia (6.13%), Amazon (3.57%), Meta (2.57%)",
            "currency": "USD",
            "countries": "United States",
            "risk_metrics": "5-year Beta: 2.99, P/E Ratio: 54.73",
            "underlying_index": "S&P 500 Index (3x leverage)",
            "cost": "$189.23",
            "managing_company": "Direxion",
            "political_outlook": "Trump’s presidency may benefit U.S. equities through reduced corporate taxes and protectionist policies.",
            "economic_outlook": "Rate reductions by the Federal Reserve may encourage equity investments."
        },
        "XLE": {
            "title": "(XLE) The Energy Select Sector SPDR Fund",
            "category": "Commodities",
            "exposure": "Focuses on companies within natural gas, oil, fuels, and energy services.",
            "key_contributors": "ExxonMobil (21.37%), Chevron (15.67%), ConocoPhillips (7.85%), Williams Companies (4.84%)",
            "currency": "USD",
            "countries": "United States",
            "risk_metrics": "5-year Beta: 0.68, P/E Ratio: 15.12",
            "underlying_index": "Energy Select Sector Index",
            "cost": "$92.56",
            "managing_company": "State Street Global Advisors Funds Management Inc.",
            "economic_outlook": "Higher domestic production and inflation support energy sector growth."
        },
        "EEM": {
            "title": "(EEM) iShares MSCI Emerging Markets ETF",
            "category": "Emerging Markets Equity",
            "exposure": "Largest companies across multiple emerging markets.",
            "key_contributors": "TSMC (10.35%), Tencent (4.28%), Samsung (2.29%), Alibaba (2.23%)",
            "currency": "USD",
            "countries": "China, India, Taiwan, South Korea, and others",
            "risk_metrics": "3-year Beta: 0.71, P/E Ratio: 16.57",
            "underlying_index": "MSCI Emerging Markets Index",
            "ratings": "MSCI ESG: A, Morningstar: 3 stars",
            "cost": "$43.97",
            "fees": "0.70%",
            "managing_company": "BlackRock iShares",
            "political_outlook": "Tariffs may negatively impact economies within this ETF.",
            "economic_outlook": "Major contributors face challenges from global shifts in production."
        },
        "SHV": {
            "title": "(SHV) iShares Short Treasury Bond ETF",
            "category": "Developed Markets Fixed Income",
            "exposure": "U.S. Treasury Bills, USD cash, and Treasury SL Agency funds.",
            "key_contributors": "Treasury Bills (101.09%), BLK CSH FND Treasury SL Agency (0.37%), USD cash (-1.46%)",
            "currency": "USD",
            "countries": "United States",
            "risk_metrics": "Duration: 0.27, Convexity: 0, 5-year Beta: 0.01",
            "underlying_index": "ICE Short US Treasury Securities Index",
            "ratings": "MSCI ESG: A",
            "cost": "$110.16",
            "fees": "0.15%",
            "managing_company": "BlackRock iShares",
            "economic_outlook": "Higher inflation may lead to rate hikes, but short duration minimizes sensitivity."
        }
    }

# Set page configuration
st.set_page_config(page_title="ETF Information Viewer", layout="wide")

# Sidebar for user selection
st.sidebar.header("Select an ETF to view information")
etf_list = list(get_etf_info().keys())
selected_etf = st.sidebar.selectbox("Choose ETF", etf_list)

# Display ETF information
if selected_etf:
    etf_info = get_etf_info()[selected_etf]
    st.title(etf_info["title"])
    st.subheader(etf_info["category"])

    st.write("### Key Details")
    st.write(f"**Exposure:** {etf_info['exposure']}")
    st.write(f"**Key Contributors:** {etf_info['key_contributors']}")
    st.write(f"**Currency Denomination:** {etf_info['currency']}")
    st.write(f"**Countries:** {etf_info['countries']}")
    st.write(f"**Risk Metrics:** {etf_info['risk_metrics']}")
    st.write(f"**Underlying Index:** {etf_info['underlying_index']}")

    if "ratings" in etf_info:
        st.write(f"**Ratings:** {etf_info['ratings']}")

    st.write(f"**Cost (as of Dec 5, 2024):** {etf_info['cost']}")
    if "fees" in etf_info:
        st.write(f"**Fees:** {etf_info['fees']}")

    st.write(f"**Managing Company:** {etf_info['managing_company']}")

    st.write("### Outlook")
    st.write(f"**Political Outlook:** {etf_info['political_outlook']}")
    st.write(f"**Economic Outlook:** {etf_info['economic_outlook']}")

# Styling for professional appearance
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    h1 {
        font-family: 'Arial', sans-serif;
        color: #003366;
    }
    h2, h3, h4 {
        color: #00509e;
    }
    </style>
    """,
    unsafe_allow_html=True
)
