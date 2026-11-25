import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

from src.mongo_loader import load_mongo_data
from src.zones import zones, connections


st.header("Electricity Transfers")

# Load electricity transfer data
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

    # Filter data by selected connection
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

    if connection_df.empty:
        st.warning("No data available for this connection.")
        st.stop()

    years = sorted(
        connection_df["timestamp"].dt.year.unique(),
        reverse=True
    )

    year = st.selectbox("Select year", years)

    # Filter by selected year
    year_df = connection_df[
        connection_df["timestamp"].dt.year == year
    ].copy()

    # Define consistent labels and colours for both plots
    export_label = f"Export ({area_a} to {area_b})"
    import_label = f"Import ({area_b} to {area_a})"

    colour_mapping = {
        export_label: "#38BDF8",
        import_label: "#F87171"
    }

    # Group by direction and sum energy
    pie_df = (
        year_df.groupby(["from_area", "to_area"])["energy_mwh"]
        .sum()
        .reset_index(name="total_energy_mwh")
    )

    pie_df["direction"] = pie_df["from_area"].apply(
        lambda x: export_label
        if x == zones[area_a]
        else import_label
    )

    # Interactive pie chart
    if pie_df["total_energy_mwh"].sum() > 0 and (
        pie_df["total_energy_mwh"] >= 0
    ).all():

        fig_pie = px.pie(
            pie_df,
            names="direction",
            values="total_energy_mwh",
            color="direction",
            color_discrete_map=colour_mapping,
            title=f"{area_a}–{area_b} ({year})"
        )

        fig_pie.update_traces(
            textinfo="percent",
            hovertemplate=(
                "%{label}<br>"
                "Energy: %{value:,.0f} MWh<br>"
                "Share: %{percent}"
                "<extra></extra>"
            )
        )

        fig_pie.update_layout(
            height=450,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.05,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.info("No valid electricity exchange totals for the selected year.")


with right_col:
    st.subheader("Electricity Exchange Over Time")

    # Only display months with available observations
    available_months = sorted(
        year_df["timestamp"].dt.month.unique()
    )

    months = [
        calendar.month_name[month]
        for month in available_months
    ]

    selected_months = st.pills(
        "Select months",
        months,
        selection_mode="multi",
        default=[months[0]]
    )

    if selected_months:

        month_numbers = [
            list(calendar.month_name).index(month)
            for month in selected_months
        ]

        # Filter by selected months
        month_df = year_df[
            year_df["timestamp"].dt.month.isin(month_numbers)
        ].copy()

        # Aggregate observations by hour and direction
        month_df["hour"] = month_df["timestamp"].dt.floor("h")

        hourly_df = (
            month_df.groupby(
                ["hour", "from_area", "to_area"]
            )["energy_mwh"]
            .sum()
            .reset_index()
            .sort_values("hour")
        )

        hourly_df["direction"] = hourly_df["from_area"].apply(
            lambda x: export_label
            if x == zones[area_a]
            else import_label
        )

        # Preserve gaps between missing or unselected periods
        hourly_df = hourly_df.pivot(
            index="hour",
            columns="direction",
            values="energy_mwh"
        )

        hourly_df = hourly_df.asfreq("h")

        hourly_df = (
            hourly_df.reset_index()
            .melt(
                id_vars="hour",
                var_name="direction",
                value_name="energy_mwh"
            )
        )

        # Interactive time series
        fig_line = px.line(
            hourly_df,
            x="hour",
            y="energy_mwh",
            color="direction",
            color_discrete_map=colour_mapping,
            title=f"{area_a}–{area_b} ({year})",
            labels={
                "hour": "Date",
                "energy_mwh": "Energy transferred per hour (MWh)",
                "direction": "Direction"
            }
        )

        fig_line.update_traces(
            connectgaps=False,
            line=dict(width=1.5),
            hovertemplate="%{y:,.2f} MWh"
        )

        fig_line.update_layout(
            height=450,
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.15,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig_line, use_container_width=True)

    else:
        st.info("Select at least one month to display electricity transfers.")


with st.expander("Data Source"):
    st.write(
        "Electricity exchange data retrieved from the "
        "ENTSO-E Transparency Platform API. "
        "The data was processed using Apache Spark, "
        "stored in Cassandra and MongoDB, "
        "and retrieved from MongoDB Atlas for visualization."
    )