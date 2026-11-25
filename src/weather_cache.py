import streamlit as st
from src.weather_loader import load_cached_weather
from src.weather_analysis import weather_spc, weather_lof, sliding_window_correlation


@st.cache_data
def cached_weather_spc(df, variable, cutoff, n_std):
    return weather_spc(df, variable, cutoff, n_std)


@st.cache_data
def cached_weather_lof(df, variable, contamination):
    return weather_lof(df, variable, contamination)

@st.cache_data
def cached_swc(df, weather_variable, window, lag):
    return sliding_window_correlation(
        df,
        weather_variable,
        window=window,
        lag=lag
    )


@st.cache_data(ttl=600)
def check_weather_availability(region, start_date, end_date,
                               resolution, n_locations):

    return load_cached_weather(
        region,
        start_date,
        end_date,
        resolution=resolution,
        n_locations=n_locations
    )