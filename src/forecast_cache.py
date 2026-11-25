import streamlit as st

from src.forecasting import forecast_reservoir


@st.cache_data(max_entries=32)
def cached_forecast(df, **settings):
    return forecast_reservoir(df, **settings)