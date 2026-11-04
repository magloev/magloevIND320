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
    This dashboard is used to provide insights into energy data from the Norwegian and European
    electricity systems. 
    The application includes following components:
    - **Reservoir data** Containing first month data from the different areas.
    - **Plots** Contains plots of various parameters from the NVE Magasinstatistikk API.
    - **Transfer data** Pie-chart and line-plot of Exchanges between Norwegian and foreign countries retrieved
    from ENTSO-E API.
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