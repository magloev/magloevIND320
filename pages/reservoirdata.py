import streamlit as st
import pandas as pd
from src.data_loader import load_reservoir_data

st.title("Reservoir Data")
#Loading the reservoir data, using data_loader.py file
df = load_reservoir_data()
area_type = st.radio(
    "Select area type",
    ["NO", "EL", "VASS"],
    horizontal=True
)

df_filtered = df[df["area_type"] == area_type].copy()

#Finds first date to display the first month (first four weeks)
start_data = df_filtered[
    (df_filtered["iso_year"] == df_filtered["iso_year"].min()) & (df_filtered   ["iso_week"].between(1,4))
]

columns = {
    "Fill level (%)": "fill_level",
    "Stored energy (TWh)": "stored_energy_TWh",
    "Fill level in previous week (%)": "fill_level_prev_week",
    "Change in fill level (%)": "fill_level_change"
}

chart_data = pd.DataFrame({"variable": list(columns.keys())})

for area_id, group in start_data.groupby("area_id"):
    group = group.sort_values("date")

    chart_data[f"{area_type}{area_id}"] = [
        group[column].tolist()
        for column in columns.values()
    ]

#Displays the first month using the LineChartColumn. 
st.dataframe(
    chart_data,
    column_config={
        column: st.column_config.LineChartColumn(column)
        for column in chart_data.columns
        if column != "variable"
    },
    hide_index=True
)