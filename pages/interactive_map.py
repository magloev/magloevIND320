import streamlit as st
import plotly.graph_objects as go
import json

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

selected_area = st.session_state["area_id"]

line_widths = [
    5 if area == selected_area else 1
    for area in area_ids
]

line_colors = [
    "red" if area == selected_area else "black"
    for area in area_ids
]

# Create map
fig = go.Figure(go.Choroplethmap(
    geojson=geojson,
    locations=area_ids,
    featureidkey="properties.area_id",
    z=area_ids,
    colorscale="Viridis",
    showscale=False,
    marker_opacity=0.3,
    marker_line_width=line_widths,
    marker_line_color=line_colors
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
