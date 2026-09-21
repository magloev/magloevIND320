import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.data_loader import load_reservoir_data

st.title("Plots")

#Loading the reservoir data, using data_loader.py file
df = load_reservoir_data()
df_no = df[df["area_type"] == "NO"].copy()


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
        "Fill level",
        "Stored energy",
        "Fill level of previous week",
        "Change in fill level",
        "All columns",
    ]
)

#Finds the first and last date of the dataset to use for the date range slider
min_date = df_no["date"].min().date()
max_date = df_no["date"].max().date()

#The "default" showing the first month of data
default_end = (pd.Timestamp(min_date) + pd.DateOffset(months=1)).date()


date_range = st.slider(
    "Select date range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, default_end),
    format="DD/MM/YYYY"
)
start_date = pd.Timestamp(date_range[0])
end_date = pd.Timestamp(date_range[1])

#Filtering the data based on the selected date range
df_filtered = df_no[
    (df_no["date"] >= start_date) &
    (df_no["date"] <= end_date)
]

if plot_selection == "Fill level":
    selected_column = "fill_level"

elif plot_selection == "Stored energy":
    selected_column = "stored_energy_TWh"

elif plot_selection == "Fill level of previous week":
    selected_column = "fill_level_prev_week"

elif plot_selection == "Change in fill level":
    selected_column = "fill_level_change"

elif plot_selection == "All columns":
    selected_column = "all_columns"

if selected_column == "all_columns":
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax1.plot(
        df_filtered["date"],
        df_filtered["fill_level"],
        label="Fill Level",
        color="blue"
    )

    ax1.set_xlabel("Date")
    ax1.set_ylabel("Fill Level", color="blue")
    ax1.tick_params(axis="x", labelrotation=45)

    ax1.grid()

    # Fill level change - right y-axis
    ax2 = ax1.twinx()

    ax2.plot(
        df_filtered["date"],
        df_filtered["fill_level_change"],
        label="Fill Level Change",
        color="red"
    )

    ax2.set_ylabel("Fill Level Change", color="red")
    ax2.tick_params(axis="x", labelrotation=45)


    plt.title("Norwegian Reservoir Fill Level and Weekly Change")

    fig.tight_layout()
    plt.show()
else:
    plt.plot(df_filtered["date"], df_filtered[selected_column])
    plt.title(f"{plot_selection} over time")
    plt.xlabel("Date")
    plt.ylabel(selected_column)
    plt.xticks(rotation=45)
    plt.grid()

plt.tight_layout()
st.pyplot(plt)