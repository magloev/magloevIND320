import streamlit as st
import plotly.graph_objects as go
import json
import pandas as pd
from src.weather_loader import load_cached_weather
from src.weather_cache import check_weather_availability

st.header("Interactive Map")

area_type = st.session_state["area_type"]
# Load GeoJSON
with open(f"data/geojson/{area_type.lower()}.geojson") as f:
    geojson = json.load(f)

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

if colour_by == "Geographical areas" or area_type != "EL":

    z_values = area_ids
    colourscale = "Viridis"
    show_scale = False

    if colour_by != "Geographical areas":
        st.info("Weather colouring is currently only available for EL areas.")

else:

    start_date, end_date = st.session_state["date_range"]

    start_date = pd.Timestamp(start_date).strftime("%Y-%m-%d")
    end_date = pd.Timestamp(end_date).strftime("%Y-%m-%d")

    for area in area_ids:

        region = f"NO {area}"

        df_weather, missing_dates = load_cached_weather(
            region,
            start_date,
            end_date,
            resolution="daily",
            n_locations=100
        )

        if colour_by == "Temperature":
            values = df_weather["temperature_2m_mean"]
        else:
            values = df_weather["precipitation_sum"]

        if len(missing_dates) > 0 or values.isna().any():
            missing_areas.append(area)
            continue

        if colour_by == "Temperature":
            weather_values[area] = values.mean()
        else:
            weather_values[area] = values.sum()

    z_values = [weather_values.get(area) for area in area_ids]

    colourscale = "RdYlBu_r" if colour_by == "Temperature" else "Blues"
    show_scale = bool(weather_values)

if missing_areas:
    missing_regions = ", ".join(
        f"NO{area}" for area in missing_areas
    )

    st.info(
        f"Incomplete weather data for: {missing_regions}. "
        "Visit the Weather Data page to download missing data."
    )

selected_area = st.session_state["area_id"]

line_widths = [
    5 if area == selected_area else 1
    for area in area_ids
]

line_colors = [
    "red" if area == selected_area else "black"
    for area in area_ids
]

if colour_by == "Temperature":
    colorbar_title = "Temperature (°C)"
elif colour_by == "Precipitation":
    colorbar_title = "Precipitation (mm)"
else:
    colorbar_title = ""

# Create map
fig = go.Figure()

# Areas with available data
available_indices = [
    i for i, area in enumerate(area_ids)
    if area not in missing_areas
]

if available_indices:
    fig.add_trace(go.Choroplethmap(
        geojson=geojson,
        locations=[area_ids[i] for i in available_indices],
        featureidkey="properties.area_id",
        z=[z_values[i] for i in available_indices],
        colorscale=colourscale,
        showscale=show_scale,
        marker_opacity=0.3,
        marker_line_width=[line_widths[i] for i in available_indices],
        marker_line_color=[line_colors[i] for i in available_indices],
        colorbar=dict(title=colorbar_title)
    ))

# Areas with missing data
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
        hovertemplate="Area %{location}<br>No weather data<extra></extra>"
    ))

fig.update_layout(
    map_style="carto-positron",
    map_center={"lat": 64.5, "lon": 15},
    map_zoom=3.5,
    height=700,
    margin=dict(l=0, r=0, t=0, b=0)
)

def select_area():
    points = st.session_state["interactive_map"].selection.points

    if points:
        st.session_state["area_id"] = points[-1]["location"]

event = st.plotly_chart(
    fig,
    use_container_width=True,
    on_select=select_area,
    selection_mode="points",
    key="interactive_map"
)
