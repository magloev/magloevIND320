import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.data_loader import load_reservoir_data
from src.reservoir_analysis import reservoir_stl, reservoir_spectrogram

st.title("Reservoir Time Series Analysis")

area_type = st.session_state["area_type"]
area_id = st.session_state["area_id"]
date_range = st.session_state["date_range"]

df = load_reservoir_data()
df["date"] = pd.to_datetime(df["date"])

start_date, end_date = date_range

df_filtered = df[
    (df["area_type"] == area_type) &
    (df["area_id"].astype(str) == str(area_id)) &
    (df["date"] >= pd.to_datetime(start_date)) &
    (df["date"] <= pd.to_datetime(end_date))
].sort_values("date")

fill_level = df_filtered.set_index("date")["fill_level"].dropna()

st.caption(
    f"Area: {area_type} {area_id} | "
    f"Period: {start_date} to {end_date}"
)

st.write(f"Weekly observations: {len(fill_level)}")

tab1, tab2 = st.tabs([
    "STL Decomposition",
    "Spectrogram"
])

area_label = f"{area_type} {area_id}"

with tab1:
    st.subheader("Seasonal-Trend Decomposition using LOESS")

    st.write(
        "STL separates reservoir filling levels into trend, seasonal "
        "and residual components, allowing us to investigate long-term "
        "changes and recurring annual patterns."
    )

    seasonal = st.slider(
        "Seasonal smoothing window (weeks)",
        min_value=7,
        max_value=53,
        value=13,
        step=2
    )

    trend = st.slider(
        "Trend smoothing window (weeks)",
        min_value=55,
        max_value=209,
        value=105,
        step=2
    )

    robust = st.checkbox(
        "Robust decomposition",
        value=True
    )

    if len(fill_level) < 104:
        st.warning(
            "Select at least two years of weekly data for a meaningful "
            "annual STL decomposition."
        )
    else:
        fig_stl, result_stl = reservoir_stl(
            fill_level,
            seasonal=seasonal,
            trend=trend,
            robust=robust,
            area=area_label
        )

        st.pyplot(fig_stl)
        plt.close(fig_stl)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Mean trend",
            f"{result_stl.trend.mean():.3f}"
        )

        col2.metric(
            "Seasonal variation (std.)",
            f"{result_stl.seasonal.std():.3f}"
        )

        col3.metric(
            "Residual variation (std.)",
            f"{result_stl.resid.std():.3f}"
        )

with tab2:
    st.subheader("Reservoir Spectrogram")

    st.write(
        "The spectrogram uses the Short-Time Fourier Transform (STFT) "
        "to investigate how the frequency content of reservoir filling "
        "levels changes over time."
    )

    nperseg = st.slider(
        "Window length (weeks)",
        min_value=52,
        max_value=208,
        value=104,
        step=52,
    )

    noverlap = st.slider(
        "Window overlap (weeks)",
        min_value=0,
        max_value=nperseg - 1,
        value=nperseg // 2
    )

    if len(fill_level) < nperseg:
        st.warning(
            f"Select at least {nperseg} weekly observations "
            "or reduce the window length."
        )
    else:
        fig_spec, result_spec = reservoir_spectrogram(
            fill_level,
            nperseg=nperseg,
            noverlap=noverlap
        )

        st.pyplot(fig_spec)
        plt.close(fig_spec)