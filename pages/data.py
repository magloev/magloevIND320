import streamlit as st
import pandas as pd

st.title("Reservoir Data")

@st.cache_data
def load_data():
    df = pd.read_csv('data/reservoirs.csv')
    return df

df = load_data()

df = df.rename(columns={
    "dato_Id": "date",
    "omrType": "area_type",
    "omrnr": "area_id",
    "iso_aar": "iso_year",
    "iso_uke": "iso_week",
    "fyllingsgrad": "fill_level",
    "kapasitet_TWh": "capacity_TWh",
    "fylling_TWh": "stored_energy_TWh",
    "neste_Publiseringsdato": "next_publication_date",
    "fyllingsgrad_forrige_uke": "fill_level_prev_week",
    "endring_fyllingsgrad": "fill_level_change"
})

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values(by="date")

df_no = df[
    df["area_type"] == "NO"
].copy()

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