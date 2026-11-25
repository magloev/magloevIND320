import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from src.data_loader import load_reservoir_data


st.header("Reservoir Data")

# Load reservoir data
df = load_reservoir_data()

# Get global selections
area_type = st.session_state["area_type"]
area_id = st.session_state["area_id"]
date_range = st.session_state["date_range"]

# Define available variables
column_mapping = {
    "Fill level (%)": "fill_level",
    "Stored energy (TWh)": "stored_energy_TWh",
    "Fill level in previous week (%)": "fill_level_prev_week",
    "Change in fill level (pp)": "fill_level_change",
    "All columns": "all_columns"
}

plot_selection = st.selectbox(
    "Select data to display",
    list(column_mapping.keys())
)

selected_column = column_mapping[plot_selection]

df["date"] = pd.to_datetime(df["date"])

if len(date_range) != 2:
    st.info("Please select both a start and end date.")
    st.stop()

start_date, end_date = date_range

# Filter data according to global selections
df_filtered = df[
    (df["date"] >= start_date) &
    (df["date"] <= end_date) &
    (df["area_type"] == area_type) &
    (df["area_id"] == area_id)
].copy()

df_filtered = df_filtered.sort_values("date")

if df_filtered.empty:
    st.warning("No reservoir data available for this selection.")
    st.stop()

st.caption(
    f"Area: {area_type}{area_id} | "
    f"Period: {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}"
)

# Display fill level and weekly change together
if selected_column == "all_columns":

    fig = make_subplots(
        specs=[[{"secondary_y": True}]]
    )

    fig.add_trace(
        go.Scatter(
            x=df_filtered["date"],
            y=df_filtered["fill_level"],
            mode="lines",
            name="Fill level",
            line=dict(color="#38BDF8"),
            hovertemplate="%{y:.2%}<extra></extra>"
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_filtered["date"],
            y=df_filtered["fill_level_change"] * 100,
            mode="lines",
            name="Weekly change",
            line=dict(color="#F87171", dash="dash"),
            hovertemplate="%{y:.2f} pp<extra></extra>"
        ),
        secondary_y=True
    )

    fig.update_yaxes(
        title_text="Fill level (%)",
        tickformat=".0%",
        secondary_y=False
    )

    fig.update_yaxes(
        title_text="Weekly change (pp)",
        secondary_y=True,
        showgrid=False
    )

    fig.update_layout(
        title="Reservoir Fill Level and Weekly Change"
    )

# Display a single selected variable
else:

    values = df_filtered[selected_column]

    if selected_column == "fill_level_change":
        values = values * 100
        hover_format = "%{y:.2f} pp"

    elif selected_column == "stored_energy_TWh":
        hover_format = "%{y:.2f} TWh"

    else:
        hover_format = "%{y:.2%}"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_filtered["date"],
        y=values,
        mode="lines",
        name=plot_selection,
        line=dict(color="#38BDF8"),
        hovertemplate=hover_format + "<extra></extra>"
    ))

    fig.update_layout(
        title=f"{plot_selection} over time",
        yaxis_title=plot_selection
    )

    if selected_column in ["fill_level", "fill_level_prev_week"]:
        fig.update_yaxes(tickformat=".0%")

# Common figure settings
fig.update_layout(
    xaxis_title="Date",
    height=500,
    hovermode="x unified",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)