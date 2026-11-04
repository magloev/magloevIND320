import streamlit as st

from src.weather_loader import aggregate_weather

st.title("Outlier & Anomaly Detection")

# Temporary override of the global selectors
region = "NO3"
start_date = "2024-01-01"
end_date = "2024-12-31"

# Load hourly regional weather averages
df_weather = aggregate_weather(region, start_date, end_date)

# Create analysis tabs
tab1, tab2 = st.tabs(["SPC / Outliers", "LOF / Anomalies"])

with tab1:
    st.subheader("Statistical Process Control")
    st.dataframe(df_weather.head())

with tab2:
    st.subheader("Local Outlier Factor")
    st.write("LOF analysis will go here.")