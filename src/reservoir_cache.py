import streamlit as st

from src.reservoir_analysis import (
    reservoir_stl,
    reservoir_spectrogram
)


@st.cache_data(max_entries=32)
def cached_reservoir_stl(
    fill_level, seasonal, trend, robust, area
):
    return reservoir_stl(
        fill_level,
        seasonal=seasonal,
        trend=trend,
        robust=robust,
        area=area
    )


@st.cache_data(max_entries=32)
def cached_reservoir_spectrogram(
    fill_level, nperseg, noverlap, area
):
    return reservoir_spectrogram(
        fill_level,
        nperseg=nperseg,
        noverlap=noverlap,
        area=area
    )