import streamlit as st
import pandas as pd


@st.cache_data
def load_reservoir_data():
    df = pd.read_csv('data/reservoirs.csv')

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

    return df


