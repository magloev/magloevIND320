import streamlit as st

from src.weather_loader import aggregate_weather
from src.weather_analysis import precipitation_spc, temperature_lof

st.title("Weather Anomaly Detection")

region = "NO 3"
start_date = "2024-01-01"
end_date = "2024-12-31"

st.caption(f"Region: {region} | Period: {start_date} to {end_date}")

df_weather = aggregate_weather(region, start_date, end_date)

tab1, tab2 = st.tabs([
    "Precipitation SPC",
    "Temperature LOF"
])

with tab1:
    st.subheader("Precipitation — Statistical Process Control")

    st.write(
        "Statistical Process Control (SPC) identifies unusual precipitation "
        "observations using DCT high-pass filtering and robust control limits."
    )

    cutoff = st.slider(
        "DCT cutoff",
        min_value=5,
        max_value=200,
        value=30,
        step=5
    )

    n_std = st.slider(
        "Control limit multiplier",
        min_value=1.0,
        max_value=5.0,
        value=3.0,
        step=0.5
    )

    fig_spc, summary_spc = precipitation_spc(
        df_weather,
        cutoff=cutoff,
        n_std=n_std
    )

    st.pyplot(fig_spc)

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
    st.subheader("Temperature — Local Outlier Factor")

    st.write(
        "Local Outlier Factor (LOF) identifies temperature observations "
        "that differ from their neighboring observations."
    )

    contamination = st.slider(
        "Contamination (%)",
        min_value=0.5,
        max_value=10.0,
        value=1.0,
        step=0.5
    )

    fig_lof, summary_lof = temperature_lof(
        df_weather,
        contamination=contamination / 100
    )

    st.pyplot(fig_lof)

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
        "Mean temperature",
        f'{summary_lof["mean_temperature"]:.2f} °C'
    )

    with st.expander("Additional LOF statistics"):
        st.write(summary_lof)