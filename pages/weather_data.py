import streamlit as st
import pandas as pd
from src.weather_cache import check_weather_availability
from src.weather_loader import aggregate_weather



st.header("Weather Data")

st.write(
    "Manage historical ERA5 temperature and precipitation "
    "data from Open-Meteo."
)

resolution = st.radio(
    "Temporal resolution",
    ["daily", "hourly"],
    horizontal=True
)

n_locations = st.radio(
    "Number of sampling locations",
    [100, 1000],
    horizontal=True
)

allow_download = resolution == "daily" and n_locations == 100

if not allow_download:
    st.info(
        "New downloads are restricted to daily data with "
        "100 sampling locations due to API limitations "
        "and computational requirements. Previously "
        "downloaded data can still be used."
    )

area_type = st.session_state["area_type"]
area_id = st.session_state["area_id"]
start_date, end_date = st.session_state["date_range"]

if area_type != "EL":
    st.info("Weather data is currently only available for electricity price areas (EL).")
    st.stop()

region = f"NO {area_id}"

start_date = pd.Timestamp(start_date).strftime("%Y-%m-%d")
end_date = pd.Timestamp(end_date).strftime("%Y-%m-%d")

st.write(f"**Selected region:** {region}")
st.write(f"**Selected period:** {start_date} to {end_date}")

df_cached, missing_dates = check_weather_availability(
    region,
    start_date,
    end_date,
    resolution,
    n_locations
)

available = len(df_cached)
missing = len(missing_dates)
total = available + missing

coverage = available / total if total > 0 else 0

col1, col2, col3 = st.columns(3)

col1.metric("Available observations", available)
col2.metric("Missing observations", missing)
col3.metric("Data coverage", f"{coverage:.1%}")

st.progress(coverage)

if missing == 0:
    st.success("All requested weather data is available.")

elif allow_download:
    st.warning(
        f"{missing} daily observations are missing "
        f"for {region}."
    )

    if st.button("Download missing data"):

        with st.spinner(f"Downloading weather data for {region}..."):
            try:
                aggregate_weather(
                    region,
                    start_date,
                    end_date,
                    resolution=resolution,
                    n_locations=n_locations,
                    allow_download=True
                )

            except Exception as e:
                st.error(f"Download failed: {e}")

            else:
                check_weather_availability.clear()
                st.rerun()

else:
    st.warning(
        "Data is missing, but new downloads are disabled "
        "for this configuration."
    )