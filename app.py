import streamlit as st
import pandas as pd
from src.data_loader import load_reservoir_data
from src.global_selector import global_selectors

st.set_page_config(
    page_title="IND320 Dashboard",
    layout="wide"
)

st.title("IND320 Dashboard")

def home():

    st.header("IND320 – Data to Decision")

    st.markdown("""
    The project combines Norwegian reservoir data, electricity transfers
    and meteorological observations to explore relationships between
    weather, energy and reservoir filling levels.
    """)

    st.subheader("Explore the application")

    st.markdown("""
    **Interactive Map**

    Explore Norwegian reservoir areas geographically and visualise average
    temperature and accumulated precipitation over a selected period.

    **Data Overview**

    - **Reservoir Data:** Historical reservoir filling levels and weekly changes.
    - **Electricity Transfers:** Electricity flows between bidding zones.
    - **Weather Data:** Historical temperature and precipitation, data coverage
      and downloading of missing observations.

    **Data Analysis**

    - **Anomaly Detection:** Detection of unusual weather observations
      using SATV/SPC and Local Outlier Factor.
    - **Time Series Analysis:** STL decomposition and spectrograms of
      reservoir filling levels.
    - **Sliding Window Correlation:** Investigation of seasonal and lagged
      relationships between weather and reservoir filling changes.

    **Prediction**

    - **Reservoir Forecasting:** Configurable multi-week forecasting using
      River, lagged reservoir observations and optional weather variables.
    """)

    st.subheader("Using the application")

    st.markdown("""
    Use the sidebar to navigate between pages and select geographical
    areas and time periods. These selections are shared across relevant
    pages.

    Areas can also be selected directly through the interactive map.
    Individual analysis pages provide additional controls for exploring
    different parameters and model configurations.
    """)

    st.subheader("Data sources")

    st.markdown("""
    - [NVE Magasinstatistikk](https://www.nve.no/)
    - [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)
    - [Open-Meteo](https://open-meteo.com/)
    """)

    st.caption(
        "Developed as part of IND320 – Data to Decision, NMBU, Autumn 2026."
    )

# Temporary placeholders for new pages
def sliding_correlation():
    st.header("Sliding Window Correlation")


def reservoir_forecasting():
    st.header("Reservoir Forecasting")


# Navigation structure
pages = {
    "": [
        st.Page(home, title="Home", default=True),
        st.Page("pages/interactive_map.py", title="Interactive Map")
    ],
    "Data Overview": [
        st.Page("pages/plots.py", title="Reservoir Data"),
        st.Page("pages/transferdata.py", title="Electricity Transfers"),
        st.Page("pages/weather_data.py", title="Weather Data")
    ],
    "Data Analysis": [
        st.Page("pages/anomaly_detection.py", title="Anomaly Detection"),
        st.Page("pages/time_series.py", title="Time Series Analysis"),
        st.Page("pages/sliding_correlation.py", title="Sliding Window Correlation")
    ],
    "Prediction": [
        st.Page("pages/reservoir_forecasting.py", title="Reservoir Forecasting")
    ]
}

pg = st.navigation(pages, position="hidden")

with st.sidebar:
    for group, page_list in pages.items():
        if group == "":
            for page in page_list:
                st.page_link(page)
        else:
            with st.expander(group, expanded=False):
                for page in page_list:
                    st.page_link(page)

if pg.title in [
    "Home",
    "Interactive Map",
    "Reservoir Data",
    "Anomaly Detection",
    "Time Series Analysis",
    "Weather Data",
    "Sliding Window Correlation",
    "Reservoir Forecasting"
]:
    global_selectors()

pg.run()