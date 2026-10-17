import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.data_loader import load_reservoir_data

st.title("Plots")

#Loading the reservoir data, using data_loader.py file
df = load_reservoir_data()

date_range = pd.date_range(
    start=df["date"].min(),
    end=df["date"].max()
)

start_date, end_date = st.select_slider(
    "Select date range",
    options=date_range,
    value=(date_range[0], date_range[28]),
    format_func=lambda date: date.strftime("%Y-%m-%d")
)

area_type = st.radio(
    "Select area type",
    ["NO", "EL", "VASS"],
    horizontal=True
)


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

#Filtering the data based on the selected date range
df_filtered = df[
    (df["date"] >= start_date) &
    (df["date"] <= end_date) &
    (df["area_type"] == area_type)
]

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

    for area_id, group in df_filtered.groupby("area_id"):
        ax1.plot(
            group["date"],
            group["fill_level"],
            label=f"{area_type}{area_id} Fill Level"
        )

        ax2.plot(
            group["date"],
            group["fill_level_change"],
            color="red",
            linestyle="--",
            label=f"{area_type}{area_id} Change"
        )

    ax1.set_xlabel("Date")
    ax1.set_ylabel("Fill Level")
    ax2.set_ylabel("Fill Level Change")

    ax1.tick_params(axis="x", labelrotation=45)
    ax1.grid()

    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    ax1.legend(
        lines1 + lines2,
        labels1 + labels2
    )

    plt.title("Reservoir Fill Level and Weekly Change")
    fig.tight_layout()
else:
    for area_id, group in df_filtered.groupby("area_id"):
        plt.plot(
            group["date"],
            group[selected_column],
            label=f"{area_type}{area_id}"
        )

    plt.legend()
    plt.title(f"{plot_selection} over time")
    plt.xlabel("Date")
    plt.ylabel(selected_column)
    plt.xticks(rotation=45)
    plt.grid()

plt.tight_layout()
st.pyplot(plt)