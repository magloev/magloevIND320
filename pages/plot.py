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

df_no_normalized = df_no.copy()
#Normalizing columns with min-max scaling, to plot them on the same graph.
for column in columns:
    df_no_normalized[column] = (
        (df_no[column] - df_no[column].min())
        / (df_no[column].max() - df_no[column].min())
    )

fig, ax = plt.subplots(figsize=(12, 6))

for column in columns:
    ax.plot(
        df_no_normalized["date"],
        df_no_normalized[column],
        label=column
    )

ax.set_title("Norwegian reservoir data over time")
ax.set_xlabel("Date")
ax.set_ylabel("Normalized value")
ax.legend()
ax.grid()
fig.tight_layout()

st.pyplot(fig)
