import streamlit as st
import pandas as pd
from src.data_loader import load_reservoir_data

def global_selectors():
    df = load_reservoir_data()

    st.sidebar.header("Global Settings")

    area_type = st.sidebar.radio(
        "Area type",
        ["NO", "EL", "VASS"],
        key="area_type"
    )

    available_areas = sorted(
        df[df["area_type"] == area_type]["area_id"].unique()
    )

    area_id = st.sidebar.selectbox(
        "Area",
        available_areas,
        key="area_id"
    )

    df_area = df[
        (df["area_type"] == area_type) &
        (df["area_id"] == area_id)
    ]

    min_date = pd.to_datetime(df_area["date"]).min().date()
    max_date = pd.to_datetime(df_area["date"]).max().date()

    # Available dates for selected area
    date_options = sorted(
        pd.to_datetime(df_area["date"]).unique()
    )

    st.sidebar.select_slider(
        "Select date range",
        options=date_options,
        value=(date_options[0], date_options[-1]),
        format_func=lambda date: pd.Timestamp(date).strftime("%Y-%m-%d"),
        key="date_range"
    )