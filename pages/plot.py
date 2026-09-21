import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.data_loader import load_reservoir_data

st.title("Plots")

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

fig, ax1 = plt.subplots(figsize=(14, 6))

# Fill level - left y-axis
ax1.plot(
    df_no["date"],
    df_no["fill_level"],
    label="Fill Level",
    color="blue"
)

ax1.set_xlabel("Date")
ax1.set_ylabel("Fill Level", color="blue")
ax1.grid()

# Fill level change - right y-axis
ax2 = ax1.twinx()

ax2.plot(
    df_no["date"],
    df_no["fill_level_change"],
    label="Fill Level Change",
    color="red"
)

ax2.set_ylabel("Fill Level Change", color="red")

plt.title("Norwegian Reservoir Fill Level and Weekly Change")

fig.tight_layout()
st.pyplot(fig)