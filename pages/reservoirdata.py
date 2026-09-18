import streamlit as st
import pandas as pd
from src.data_loader import load_reservoir_data

st.title("Reservoir Data")

df = load_reservoir_data()
df_no = df[df["area_type"] == "NO"].copy()

start_data = df_no[
    (df_no["iso_year"] == df_no["iso_year"].min()) & (df_no["iso_week"].between(1,4))
]

chart_data = pd.DataFrame({
    "variable": [
        "Fill level",
        "Stored energy (TWh)",
        "Fill level in previous week",
        "Change in fill level"
        ],
    "values": [
        start_data["fill_level"].tolist(),
        start_data["stored_energy_TWh"].tolist(),
        start_data["fill_level_prev_week"].tolist(),
        start_data["fill_level_change"].tolist()
    ]
})

st.dataframe(
    chart_data,
    column_config={
        "values": st.column_config.LineChartColumn("First Month")
    },
    hide_index=True
)

st.write("A preview of the reservoir dataset")