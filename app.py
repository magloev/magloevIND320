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

pages = [
    st.Page(home, title="Home"),
    st.Page("pages/plots.py", title="Plots"),
    st.Page("pages/transferdata.py", title="Transfer Data"),
    st.Page("pages/anomaly_detection.py", title="Anomaly Detection"),
    st.Page("pages/time_series.py", title="Time Series Analysis")]

pg = st.navigation(pages)
if pg.title != "Transfer Data":
    global_selectors()
pg.run()