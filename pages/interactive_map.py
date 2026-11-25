import streamlit as st
import plotly.graph_objects as go
import json
import pandas as pd

from src.weather_cache import check_weather_availability


st.header("Interactive Map")

area_type = st.session_state["area_type"]

# Load and cache GeoJSON
@st.cache_data
def load_geojson(area_type):
    with open(
        f"data/geojson/{area_type.lower()}.geojson",
        encoding="utf-8"
    ) as f:
        return json.load(f)


geojson = load_geojson(area_type)

# Extract area identifiers
area_ids = [
    feature["properties"]["area_id"]
    for feature in geojson["features"]
]

colour_by = st.radio(
    "Colour map by",
    ["Geographical areas", "Temperature", "Precipitation"],
    horizontal=True
)

missing_areas = []
weather_values = {}
weather_status = []

# Geographical colouring
if colour_by == "Geographical areas" or area_type != "EL":

    z_values = area_ids
    colourscale = "Viridis"
    show_scale = False

    if colour_by != "Geographical areas":
        st.info(
            "Weather colouring is currently only available for EL areas."
        )

# Weather colouring
else:

    start_date, end_date = st.session_state["date_range"]

    start_date = pd.Timestamp(start_date).strftime("%Y-%m-%d")
    # Account for the ERA5 publication delay
    latest_weather_date = (
        pd.Timestamp.now(tz="UTC").normalize().tz_localize(None)
        - pd.Timedelta(days=7)
    )

    selected_end = pd.Timestamp(end_date)

    end_date = min(
        selected_end,
        latest_weather_date
    ).strftime("%Y-%m-%d")

    if pd.Timestamp(end_date) < selected_end:
        st.caption(
            f"Weather data displayed until {end_date} "
            "due to the ERA5 publication delay."
        )

    variable = (
        "temperature_2m_mean"
        if colour_by == "Temperature"
        else "precipitation_sum"
    )

    for area in area_ids:

        region = f"NO {int(area)}"

        df_weather, missing_dates = check_weather_availability(
            region,
            start_date,
            end_date,
            resolution="daily",
            n_locations=100
        )

        values = pd.to_numeric(
            df_weather[variable],
            errors="coerce"
        )

        missing_values = int(values.isna().sum())

        weather_status.append({
            "Region": region,
            "Available observations": len(df_weather),
            "Missing dates": len(missing_dates),
            "Missing values": missing_values
        })

        if (
            df_weather.empty
            or len(missing_dates) > 0
            or missing_values > 0
        ):
            missing_areas.append(area)
            continue

        if colour_by == "Temperature":
            weather_values[area] = values.mean()
        else:
            weather_values[area] = values.sum()

    z_values = [
        weather_values.get(area)
        for area in area_ids
    ]

    colourscale = (
        "RdYlBu_r"
        if colour_by == "Temperature"
        else "Blues"
    )

    show_scale = bool(weather_values)


# Display information about incomplete weather data
if missing_areas:

    missing_regions = ", ".join(
        f"NO{area}" for area in missing_areas
    )

    st.info(
        f"Incomplete weather data for: {missing_regions}. "
        "Check weather data coverage for the selected period."
    )

    with st.expander("Weather data availability"):
        st.dataframe(
            pd.DataFrame(weather_status),
            hide_index=True,
            use_container_width=True
        )

        st.caption(
            f"Period: {start_date} to {end_date} | "
            "Daily resolution | 100 sampling locations"
        )


# Highlight selected geographical area
selected_area = st.session_state["area_id"]

line_widths = [
    5 if area == selected_area else 1
    for area in area_ids
]

line_colors = [
    "red" if area == selected_area else "black"
    for area in area_ids
]


# Define colour bar units
if colour_by == "Temperature":
    colorbar_title = "Temperature (°C)"
elif colour_by == "Precipitation":
    colorbar_title = "Precipitation (mm)"
else:
    colorbar_title = ""


# Create map
fig = go.Figure()

available_indices = [
    i for i, area in enumerate(area_ids)
    if area not in missing_areas
]

# Areas with available data
if available_indices:

    fig.add_trace(go.Choroplethmap(
        geojson=geojson,
        locations=[area_ids[i] for i in available_indices],
        featureidkey="properties.area_id",
        z=[z_values[i] for i in available_indices],
        colorscale=colourscale,
        showscale=show_scale,
        marker_opacity=0.3,
        marker_line_width=[
            line_widths[i] for i in available_indices
        ],
        marker_line_color=[
            line_colors[i] for i in available_indices
        ],
        colorbar=dict(title=colorbar_title)
    ))


# Display areas with incomplete weather data in grey
if missing_areas:

    fig.add_trace(go.Choroplethmap(
        geojson=geojson,
        locations=missing_areas,
        featureidkey="properties.area_id",
        z=[0] * len(missing_areas),
        colorscale=[[0, "grey"], [1, "grey"]],
        showscale=False,
        marker_opacity=0.3,
        marker_line_width=[
            5 if area == selected_area else 1
            for area in missing_areas
        ],
        marker_line_color=[
            "red" if area == selected_area else "black"
            for area in missing_areas
        ],
        hovertemplate=(
            "Area %{location}<br>"
            "Incomplete weather data<extra></extra>"
        )
    ))


# Map layout
fig.update_layout(
    map_style="carto-positron",
    map_center={"lat": 64.5, "lon": 15},
    map_zoom=3.5,
    height=700,
    margin=dict(l=0, r=0, t=0, b=0)
)


# Store selected area in global session state
def select_area():

    points = st.session_state["interactive_map"].selection.points

    if points:
        st.session_state["area_id"] = points[-1]["location"]


st.plotly_chart(
    fig,
    use_container_width=True,
    on_select=select_area,
    selection_mode="points",
    key="interactive_map"
)