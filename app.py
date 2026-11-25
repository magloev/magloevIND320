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
    st.subheader("About the project")
    st.markdown("""
        ### Norwegian Energy Data Analysis

        This project explores Norwegian energy data through interactive
        visualizations, data processing, and statistical analysis.

        The project consists of three parts:

        **Part 1 – Reservoir Data**  
        Analysis and visualization of historical Norwegian reservoir
        filling levels using data from the Norwegian Water Resources
        and Energy Directorate (NVE).

        **Part 2 – Electricity Transfers**  
        Analysis of electricity imports and exports between Norwegian
        and neighboring European bidding zones using ENTSO-E data.
        The workflow incorporates Apache Spark, Cassandra, and MongoDB.

        **Part 3 – Weather and Time Series Analysis**  
        Historical ERA5 temperature and precipitation data from
        Open-Meteo are combined with reservoir data to investigate
        anomalies, seasonal patterns, and frequency characteristics.

        Statistical methods include:
        - Discrete Cosine Transform (DCT) and Statistical Process Control (SPC)
        - Local Outlier Factor (LOF)
        - Seasonal-Trend decomposition using LOESS (STL)
        - Short-Time Fourier Transform (STFT)

        Use the navigation menu to explore the datasets and analyses.
        """)

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
        st.Page(sliding_correlation, title="Sliding Window Correlation")
    ],
    "Prediction": [
        st.Page(reservoir_forecasting, title="Reservoir Forecasting")
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
    "Weather Data"
]:
    global_selectors()

pg.run()