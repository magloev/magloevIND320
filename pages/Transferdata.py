import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar
from src.mongo_loader import load_mongo_data
from src.zones import zones, connections

st.title("Electricity Exchange")

df = load_mongo_data()
df["timestamp"] = pd.to_datetime(df["timestamp"])

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Total Electricity Exchange")

    connection = st.radio(
        "Select connection",
        connections,
        format_func=lambda x: f"{x[0]}-{x[1]}",
        index=2
    )

    area_a, area_b = connection

    connection_df = df[
        (
            (df["from_area"] == zones[area_a]) &
            (df["to_area"] == zones[area_b])
        ) |
        (
            (df["from_area"] == zones[area_b]) &
            (df["to_area"] == zones[area_a])
        )
    ].copy()

    years = sorted(df["timestamp"].dt.year.unique(), reverse=True)

    year = st.selectbox("Select year", years)

    # Filter by selected year
    year_df = connection_df[
        connection_df["timestamp"].dt.year == year
    ]

    # Group by direction and sum energy
    pie_df = (
        year_df.groupby(["from_area", "to_area"])["energy_mwh"]
        .sum()
        .reset_index(name="total_energy_mwh")
    )

    labels = [
        f"Export ({area_a} to {area_b})" if area == zones[area_a]
        else f"Import ({area_b} to {area_a})"
        for area in pie_df["from_area"]
    ]

    fig, ax = plt.subplots(figsize=(6, 5))

    ax.pie(
        pie_df["total_energy_mwh"],
        labels=labels,
        autopct="%1.1f%%",
        startangle=90
    )

    ax.set_title(f"Electricity Transfers between {area_a} and {area_b} ({year})")

    st.pyplot(fig)
    plt.close(fig)

with right_col:
    st.subheader("Electricity Exchange Over Time")

    months = list(calendar.month_name)[1:]

    #Default month for 2024 is October since that is the earliest month with data.
    default_month = "October" if year == 2024 else "January"
    selected_months = st.pills(
        "Select months",
        months,
        selection_mode="multi",
        default=[default_month]
    )

    # Convert selected month names into month numbers
    month_numbers = [
        months.index(month) + 1
        for month in selected_months
    ]

    # Filter by selected year and months
    month_df = connection_df[
        (df["timestamp"].dt.year == year) &
        (df["timestamp"].dt.month.isin(month_numbers))
    ].copy()

    # Group observations by hour and direction
    month_df["hour"] = month_df["timestamp"].dt.floor("h")

    hourly_df = (
        month_df.groupby(["hour", "from_area", "to_area"])["energy_mwh"]
        .sum()
        .reset_index()
        .sort_values("hour")
    )

    hourly_df["direction"] = hourly_df["from_area"].apply(
        lambda x: f"Import {area_a} to {area_b}" if x == zones[area_a] else f"Import {area_b} to {area_a}"
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    for direction, group in hourly_df.groupby("direction"):
        ax.plot(
            group["hour"],
            group["energy_mwh"],
            label=direction,
            linewidth=1
        )

    ax.set_title(f"Electricity Transfers between {area_a} and {area_b} ({year})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Energy transferred per hour (MWh)")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

with st.expander("Data Source"):
    st.write(
        "Electricity exchange data retrieved from the "
        "ENTSO-E Transparency Platform API. "
        "The data was processed using Apache Spark, "
        "stored in Cassandra and MongoDB, "
        "and retrieved from MongoDB Atlas for visualization."
    )