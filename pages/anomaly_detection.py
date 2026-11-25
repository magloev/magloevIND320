import streamlit as st
import pandas as pd
from src.weather_cache import check_weather_availability, cached_weather_spc, cached_weather_lof
from src.weather_analysis import weather_spc, weather_lof

st.title("Weather Anomaly Detection")

area_type = st.session_state["area_type"]
area_id = st.session_state["area_id"]

if area_type != "EL":
    st.info("Weather analysis is currently only available for EL areas.")
    st.stop()

region = f"NO {area_id}"

start_date, end_date = st.session_state["date_range"]

start_date = pd.Timestamp(start_date).strftime("%Y-%m-%d")
end_date = pd.Timestamp(end_date).strftime("%Y-%m-%d")

st.caption(f"Region: {region} | Period: {start_date} to {end_date}")

resolution = st.radio(
    "Temporal resolution",
    ["daily", "hourly"],
    horizontal=True
)

n_locations = 100 if resolution == "daily" else 1000

df_weather, missing_dates = check_weather_availability(
    region,
    start_date,
    end_date,
    resolution=resolution,
    n_locations=n_locations
)

if len(missing_dates) > 0:
    st.warning(
        f"{len(missing_dates)} weather observations are missing. "
        "Visit the Weather Data page to download missing data."
    )
    st.stop()

if len(df_weather) < 5:
    st.warning("At least five observations are required for anomaly detection.")
    st.stop()

if df_weather.empty or df_weather.isna().any().any():
    st.warning("Weather data is empty or contains missing values.")
    st.stop()

weather_property = st.radio(
    "Weather property",
    ["Temperature", "Precipitation"],
    horizontal=True
)

if resolution == "daily":
    variable = (
        "temperature_2m_mean"
        if weather_property == "Temperature"
        else "precipitation_sum"
    )
else:
    variable = (
        "temperature_2m"
        if weather_property == "Temperature"
        else "precipitation"
    )

unit = "°C" if weather_property == "Temperature" else "mm"

tab1, tab2 = st.tabs([
    "Statistical Process Control (SPC)",
    "Local Outlier Factor (LOF)"
])

with tab1:
    st.subheader(f"{weather_property} — Statistical Process Control")

    st.write(
        "Statistical Process Control (SPC) identifies unusual "
        f"{weather_property.lower()} "
        "observations using DCT high-pass filtering and robust control limits."
    )

    max_cutoff = min(200, len(df_weather) - 1)

    cutoff = st.slider(
        "DCT cutoff",
        min_value=1,
        max_value=max_cutoff,
        value=min(30, max_cutoff),
        step=1
    )

    n_std = st.slider(
        "Control limit multiplier",
        min_value=1.0,
        max_value=5.0,
        value=3.0,
        step=0.5
    )

    fig_spc, summary_spc = cached_weather_spc(
        df_weather,
        variable=variable,
        cutoff=cutoff,
        n_std=n_std
    )

    st.plotly_chart(fig_spc, use_container_width=True)

    st.subheader("SPC Statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total outliers",
        summary_spc["total_outliers"]
    )

    col2.metric(
        "Outlier percentage",
        f'{summary_spc["outlier_percentage"]:.2f}%'
    )

    col3.metric(
        "Total observations",
        summary_spc["total_observations"]
    )

    with st.expander("Additional SPC statistics"):
        st.write(summary_spc)


with tab2:
    st.subheader(f"{weather_property} — Local Outlier Factor")

    st.write(
        "Local Outlier Factor (LOF) identifies "
        f"{weather_property.lower()} observations "
        "that differ from their neighboring observations."
    )

    contamination = st.slider(
        "Contamination (%)",
        min_value=0.5,
        max_value=10.0,
        value=1.0,
        step=0.5
    )

    fig_lof, summary_lof = cached_weather_lof(
        df_weather,
        variable=variable,
        contamination=contamination / 100
    )

    st.plotly_chart(fig_lof, use_container_width=True)

    st.subheader("LOF Statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total anomalies",
        summary_lof["total_anomalies"]
    )

    col2.metric(
        "Anomaly percentage",
        f'{summary_lof["anomaly_percentage"]:.2f}%'
    )

    col3.metric(
        f"Mean {weather_property.lower()}",
        f'{summary_lof["mean_value"]:.2f} {unit}'
    )

    with st.expander("Additional LOF statistics"):
        st.write(summary_lof)