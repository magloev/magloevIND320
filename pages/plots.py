import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.data_loader import load_reservoir_data

st.title("Plots")

#Loading the reservoir data, using data_loader.py file
df = load_reservoir_data()

# Get global selections
area_type = st.session_state["area_type"]
area_id = st.session_state["area_id"]
date_range = st.session_state["date_range"]

#Relevant columns to plot
columns = [
    "fill_level",
    "stored_energy_TWh",
    "fill_level_prev_week",
    "fill_level_change"
]

plot_selection = st.selectbox(
    "Select data to display",
    [
        "Fill level (%)",
        "Stored energy (TWh)",
        "Fill level in previous week (%)",
        "Change in fill level (%)",
        "All columns",
    ]
)

df["date"] = pd.to_datetime(df["date"])

if len(date_range) != 2:
    st.info("Please select both a start and end date.")
    st.stop()

start_date, end_date = date_range

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

if plot_selection == "Fill level (%)":
    selected_column = "fill_level"

elif plot_selection == "Stored energy (TWh)":
    selected_column = "stored_energy_TWh"

elif plot_selection == "Fill level in previous week (%)":
    selected_column = "fill_level_prev_week"

elif plot_selection == "Change in fill level (%)":
    selected_column = "fill_level_change"

elif plot_selection == "All columns":
    selected_column = "all_columns"

if selected_column == "all_columns":
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()

    ax1.plot(
        df_filtered["date"],
        df_filtered["fill_level"],
        label="Fill Level"
    )

    ax2.plot(
        df_filtered["date"],
        df_filtered["fill_level_change"],
        color="red",
        linestyle="--",
        label="Fill Level Change"
    )

    ax1.set_xlabel("Date")
    ax1.set_ylabel("Fill Level")
    ax2.set_ylabel("Fill Level Change")
    ax1.tick_params(axis="x", labelrotation=45)
    ax1.grid()

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    ax1.legend(lines1 + lines2, labels1 + labels2)

    ax1.set_title("Reservoir Fill Level and Weekly Change")

else:
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(
        df_filtered["date"],
        df_filtered[selected_column],
        label=f"{area_type}{area_id}"
    )

    ax.legend()
    ax.set_title(f"{plot_selection} over time")
    ax.set_xlabel("Date")
    ax.set_ylabel(selected_column)
    ax.tick_params(axis="x", labelrotation=45)
    ax.grid()

fig.tight_layout()
st.pyplot(fig)
plt.close(fig)
