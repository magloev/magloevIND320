import streamlit as st
import pandas as pd
from src.data_loader import load_reservoir_data

#These two functions are used to store and load values from the session state, 
#Instead of the button widgets storing the selection. This also makes sure we have two
#Ways to select a region: from the sidebar and from the map.
def store_value(key):
    st.session_state[key] = st.session_state["_" + key]

def load_value(key):
    st.session_state["_" + key] = st.session_state[key]


def global_selectors():
    df = load_reservoir_data()

    st.sidebar.header("Global Settings")

    # Area type
    if "area_type" not in st.session_state:
        st.session_state["area_type"] = "NO"

    load_value("area_type")

    area_type = st.sidebar.radio(
        "Area type",
        ["NO", "EL", "VASS"],
        key="_area_type",
        on_change=store_value,
        args=("area_type",)
    )

    # Available areas
    available_areas = sorted(
        df[df["area_type"] == area_type]["area_id"].unique()
    )

    if st.session_state.get("area_id") not in available_areas:
        st.session_state["area_id"] = available_areas[0]

    load_value("area_id")

    area_id = st.sidebar.selectbox(
        "Area",
        available_areas,
        key="_area_id",
        on_change=store_value,
        args=("area_id",)
    )

    # Filter selected area
    df_area = df[
        (df["area_type"] == area_type) &
        (df["area_id"] == area_id)
    ]

    date_options = sorted(
        pd.to_datetime(df_area["date"]).unique()
    )

    # Initialise or validate date range
    date_range = st.session_state.get("date_range")

    default_start = next(
        (date for date in date_options
         if pd.Timestamp(date) >= pd.Timestamp("2024-01-01")),
        date_options[0]
    )


    if date_range is None or not all(
        date in date_options for date in date_range
    ):
        st.session_state["date_range"] = (
            default_start, date_options[-1]
        )

    load_value("date_range")

    st.sidebar.select_slider(
        "Select date range",
        options=date_options,
        value=st.session_state["date_range"],
        format_func=lambda date: pd.Timestamp(date).strftime("%Y-%m-%d"),
        key="_date_range",
        on_change=store_value,
        args=("date_range",)
    )