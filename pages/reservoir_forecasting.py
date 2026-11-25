import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.data_loader import load_reservoir_data
from src.weather_cache import check_weather_availability
from src.forecast_cache import cached_forecast


st.header("Reservoir Forecasting")

st.write(
    "Forecast future reservoir filling using a River linear "
    "regression model with lagged reservoir observations "
    "and optional meteorological variables."
)

# Global selections


area_type = st.session_state["area_type"]
area_id = st.session_state["area_id"]

if area_type != "EL":
    st.info("Forecasting is currently available for EL areas.")
    st.stop()

region = f"NO{area_id}"

start_date, end_date = st.session_state["date_range"]

start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

st.caption(
    f"Region: {region} | "
    f"Selected forecast origin: {end_date:%Y-%m-%d}"
)

# Model settings


st.subheader("Model Settings")

st.caption(
    "River Linear Regression | StandardScaler | SGD"
)

use_global_period = st.checkbox(
    "Use global date range as training period",
    value=False
)

col1, col2 = st.columns(2)

with col1:

    history_years = st.slider(
        "Training history (years)",
        min_value=1,
        max_value=20,
        value=10,
        disabled=use_global_period
    )

    horizon = st.slider(
        "Forecast horizon (weeks)",
        min_value=1,
        max_value=52,
        value=12
    )

with col2:

    learning_rate = st.number_input(
        "Learning rate",
        min_value=0.001,
        max_value=0.100,
        value=0.080,
        step=0.001,
        format="%.3f"
    )

    reservoir_lags = st.multiselect(
        "Reservoir lags (weeks)",
        options=[1, 2, 3, 4, 8, 12, 26, 52],
        default=[1, 2, 4, 52]
    )

if not reservoir_lags:
    st.warning("Select at least one reservoir lag.")
    st.stop()


# Optional weather features

st.subheader("Exogenous Variables")

weather_properties = st.multiselect(
    "Meteorological variables",
    options=["Temperature", "Precipitation"],
    default=[]
)

weather_mapping = {
    "Temperature": "temperature_2m_mean",
    "Precipitation": "precipitation_sum"
}

weather_features = []

if weather_properties:

    weather_lags = st.multiselect(
        "Weather lags (weeks)",
        options=[0, 1, 2, 4, 8, 12, 26, 52],
        default=[1]
    )

    if not weather_lags:
        st.warning("Select at least one weather lag.")
        st.stop()

    weather_features = [
        (weather_mapping[prop], lag)
        for prop in weather_properties
        for lag in weather_lags
    ]

    st.caption(
        "Unknown future weather is estimated using "
        "historical averages for each week of the year."
    )

else:
    st.caption("Weather disabled — baseline reservoir model.")

# Load reservoir data


df_reservoir = load_reservoir_data()

df_region = df_reservoir[
    (df_reservoir["area_type"] == area_type) &
    (df_reservoir["area_id"] == area_id)
].copy()

df_region["date"] = pd.to_datetime(df_region["date"])

df_region = df_region[
    df_region["date"] <= end_date
].sort_values("date")

if df_region.empty:
    st.warning("No reservoir data available.")
    st.stop()

last_date = df_region.loc[
    df_region["fill_level"].notna(), "date"
].max()

if pd.isna(last_date):
    st.warning("No valid reservoir observations available.")
    st.stop()

if use_global_period:
    training_start = start_date
else:
    training_start = (
        last_date
        + pd.Timedelta(weeks=1)
        - pd.DateOffset(years=history_years)
    )

# Load optional weather data


if weather_features:

    # Include additional history for weather lag features
    weather_start = training_start - pd.Timedelta(
        weeks=max(weather_lags)
    )

    # Align start to Monday for complete ISO weeks
    weather_start = weather_start - pd.Timedelta(
        days=weather_start.dayofweek
    )

    with st.spinner("Loading historical weather data..."):

        df_weather, missing_dates = check_weather_availability(
            f"NO {area_id}",
            weather_start.strftime("%Y-%m-%d"),
            last_date.strftime("%Y-%m-%d"),
            resolution="daily",
            n_locations=100
        )

    if df_weather.empty:
        st.warning(
            "No weather data available for the selected period. "
            "Visit the Weather Data page or disable weather features."
        )
        st.stop()

    if len(missing_dates) > 0:
        st.warning(
            f"{len(missing_dates)} daily weather observations "
            "are missing. The model will train only on observations "
            "with all required features available."
        )

    df_weather = df_weather.copy()

    # Extract ISO year and week
    iso = df_weather["date"].dt.isocalendar()

    df_weather["iso_year"] = iso.year
    df_weather["iso_week"] = iso.week

    # Aggregate weather to weekly resolution
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

    # Exclude incomplete weather weeks
    df_weather_weekly = df_weather_weekly[
        (df_weather_weekly["temperature_days"] == 7) &
        (df_weather_weekly["precipitation_days"] == 7)
    ]

    if df_weather_weekly.empty:
        st.warning("No complete weekly weather observations.")
        st.stop()

    # Merge without removing historical reservoir observations
    df_region = pd.merge(
        df_region,
        df_weather_weekly[
            [
                "iso_year",
                "iso_week",
                "temperature_2m_mean",
                "precipitation_sum"
            ]
        ],
        on=["iso_year", "iso_week"],
        how="left"
    )

# Train model and generate forecast


with st.spinner("Training River model and generating forecast..."):

    try:

        df_history, df_forecast = cached_forecast(
            df_region,
            region=region,
            history_years=history_years,
            horizon=horizon,
            learning_rate=learning_rate,
            reservoir_lags=tuple(reservoir_lags),
            weather_features=tuple(weather_features),
            end_date=end_date,
            training_start=training_start
        )

    except Exception as e:

        st.error(f"Forecasting failed: {e}")
        st.stop()

# Validate predictions


predictions = df_forecast["prediction"]

if not np.isfinite(predictions).all():
    st.error("The model produced invalid predictions.")
    st.stop()

if not predictions.between(0, 1).all():
    st.warning(
        "Some predictions fall outside the physical range "
        "of 0–100%. Try adjusting the model parameters."
    )
    st.stop()

# Training information


required_features = [
    f"lag_{lag}" for lag in reservoir_lags
] + [
    f"{variable}_lag_{lag}"
    for variable, lag in weather_features
]

df_training = df_history.dropna(
    subset=required_features + ["fill_level"]
)

st.caption(
    f"Actual training period: "
    f"{df_training['date'].min():%Y-%m-%d} to "
    f"{df_training['date'].max():%Y-%m-%d} | "
    f"Training observations: {len(df_training)}"
)

# Forecast summary


st.subheader("Forecast Results")

current_level = df_history["fill_level"].iloc[-1]
predicted_level = predictions.iloc[-1]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Last observed fill level",
    f"{current_level:.1%}"
)

col2.metric(
    f"Forecast in {horizon} weeks",
    f"{predicted_level:.1%}",
    delta=f"{100 * (predicted_level - current_level):.1f} pp"
)

col3.metric(
    "Training observations",
    len(df_training)
)

# Prepare animated Plotly figure


# Display the latest year of historical observations
df_display = df_history.tail(52)

# Connect forecast line to the final historical observation
forecast_dates = [df_history["date"].iloc[-1]] + (
    df_forecast["date"].tolist()
)

forecast_values = [current_level] + (
    df_forecast["prediction"].tolist()
)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_display["date"],
    y=df_display["fill_level"],
    mode="lines",
    name="Historical observations"
))

fig.add_trace(go.Scatter(
    x=forecast_dates,
    y=forecast_values,
    mode="lines+markers",
    name="Recursive forecast",
    line=dict(color="#3B82F6", dash="dash")
))


# Animation frames
fig.frames = [
    go.Frame(
        name=str(step),
        data=[
            go.Scatter(
                x=forecast_dates[:step + 1],
                y=forecast_values[:step + 1]
            )
        ],
        traces=[1]
    )
    for step in range(1, horizon + 1)
]


# Animation controls
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Reservoir filling level",
    height=550,
    hovermode="x unified",
    margin=dict(t=75),

    updatemenus=[
        dict(
            type="buttons",
            direction="left",
            x=0,
            y=1.02,
            xanchor="left",
            yanchor="bottom",
            pad=dict(r=10, t=0),
            showactive=False,
            bgcolor="#374151",
            bordercolor="#64748b",
            font=dict(color="white"),
            buttons=[
                dict(
                    label="Play forecast",
                    method="animate",
                    args=[
                        None,
                        dict(
                            frame=dict(
                                duration=200,
                                redraw=False
                            ),
                            transition=dict(duration=0),
                            fromcurrent=False,
                            mode="immediate"
                        )
                    ]
                ),
                dict(
                    label="Pause",
                    method="animate",
                    args=[
                        [None],
                        dict(
                            frame=dict(duration=0),
                            transition=dict(duration=0),
                            mode="immediate"
                        )
                    ]
                )
            ]
        )
    ]
)

fig.update_xaxes(
    range=[
        df_display["date"].min(),
        df_forecast["date"].max()
    ]
)

fig.update_yaxes(
    tickformat=".0%",
    range=[
        min(0, predictions.min()),
        max(1, predictions.max())
    ]
)

st.subheader(f"Reservoir Filling Forecast — {region}")
st.plotly_chart(fig, use_container_width=True)

# Underlying data


with st.expander("View forecast data"):
    st.dataframe(df_forecast)

with st.expander("View training data"):
    st.dataframe(df_training)
