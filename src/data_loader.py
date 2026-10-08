import streamlit as st
import pandas as pd
import requests


@st.cache_data
def load_reservoir_data():
    url = "https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData"

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    df = pd.DataFrame(response.json())


    #renaming columns to english, readable names
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

    #Sort data by date, as csv file is unsorted. important for plotting.
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by="date")

    return df


