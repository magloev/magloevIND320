import streamlit as st
import pandas as pd

from src.data_loader import load_reservoir_data
from src.weather_cache import check_weather_availability, cached_swc
from src.weather_analysis import plot_swc


st.header("Sliding Window Correlation")

st.write(
    "Sliding Window Correlation (SWC) explores how the relationship "
    "between weather conditions and changes in reservoir filling varies "
    "over time."
)

# Global selections
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


# Load weather data
df_weather, missing_dates = check_weather_availability(
    region,
    start_date,
    end_date,
    resolution="daily",
    n_locations=100
)

if len(missing_dates) > 0 or df_weather.empty:
    st.warning(
        "Weather data is missing. Visit the Weather Data page "
        "to download missing observations."
    )
    st.stop()


# Extract ISO year and week
df_weather = df_weather.copy()

iso = df_weather["date"].dt.isocalendar()

df_weather["iso_year"] = iso.year
df_weather["iso_week"] = iso.week


# Aggregate daily weather into weekly observations
df_weather_weekly = (
    df_weather.groupby(["iso_year", "iso_week"])
    .agg(
        temperature_2m_mean=("temperature_2m_mean", "mean"),
        precipitation_sum=("precipitation_sum", "sum"),
        temperature_days=("temperature_2m_mean", "count"),
        precipitation_days=("precipitation_sum", "count")
    )
    .reset_index()
)

# Retain complete weeks
df_weather_weekly = df_weather_weekly[
    (df_weather_weekly["temperature_days"] == 7) &
    (df_weather_weekly["precipitation_days"] == 7)
]


# Load reservoir data
df_reservoir = load_reservoir_data()

df_region = df_reservoir[
    (df_reservoir["area_type"] == area_type) &
    (df_reservoir["area_id"] == area_id)
].copy()

df_region = df_region[
    df_region["date"].between(start_date, end_date)
]


# Merge reservoir and weather data
df_swc = pd.merge(
    df_region,
    df_weather_weekly,
    on=["iso_year", "iso_week"],
    how="inner"
)


# Prepare SWC dataframe
df_swc = df_swc[
    [
        "date",
        "fill_level",
        "temperature_2m_mean",
        "precipitation_sum"
    ]
].copy()

df_swc = df_swc.sort_values("date")
df_swc = df_swc.set_index("date")

df_swc["fill_level_change"] = df_swc["fill_level"].diff()


# Check number of observations
if len(df_swc) < 6:
    st.warning(
        "Select a longer date range. At least six weekly "
        "observations are required."
    )
    st.stop()


# Check that observations are consecutive
if not df_swc.index.to_series().diff().dropna().eq(
    pd.Timedelta(weeks=1)
).all():
    st.warning("The dataset contains gaps in its weekly observations.")
    st.stop()


# Weather property selector
weather_property = st.radio(
    "Weather property",
    ["Temperature", "Precipitation"],
    horizontal=True
)

weather_variable = (
    "temperature_2m_mean"
    if weather_property == "Temperature"
    else "precipitation_sum"
)


# Lag and window settings
col1, col2 = st.columns(2)

with col1:
    lag = st.slider(
        "Weather lag (weeks)",
        min_value=0,
        max_value=min(12, len(df_swc) - 5),
        value=0
    )

max_window = min(52, len(df_swc) - max(1, lag))

with col2:
    window = st.slider(
        "Window length (weeks)",
        min_value=4,
        max_value=max_window,
        value=min(12, max_window)
    )


# Calculate sliding window correlation
swc = cached_swc(
    df_swc,
    weather_variable,
    window,
    lag
)


# Display interactive figure
fig = plot_swc(
    swc,
    weather_variable,
    window,
    lag
)

st.plotly_chart(fig, use_container_width=True)


# Summary statistics
st.subheader("Correlation Statistics")

valid_swc = swc.dropna()

if not valid_swc.empty:
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Mean correlation",
        f"{valid_swc.mean():.3f}"
    )

    col2.metric(
        "Minimum correlation",
        f"{valid_swc.min():.3f}"
    )

    col3.metric(
        "Maximum correlation",
        f"{valid_swc.max():.3f}"
    )
else:
    st.info("No valid correlations for the selected settings.")


# Display underlying dataset
with st.expander("View underlying data"):
    st.dataframe(df_swc)

    st.write("Weekly observations:", len(df_swc))


# Interpretation
st.caption(
    "A positive lag compares current reservoir changes with earlier "
    "weather conditions. Correlation does not imply causation."
)