import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy.fft import dct, idct
from sklearn.neighbors import LocalOutlierFactor

WEATHER_PROPERTIES = {
    "temperature_2m": ("Temperature", "°C"),
    "precipitation": ("Precipitation", "mm"),
    "temperature_2m_mean": ("Temperature", "°C"),
    "precipitation_sum": ("Precipitation", "mm")
}

def weather_spc(df, variable="temperature_2m", cutoff=30, n_std=3):

    name, unit = WEATHER_PROPERTIES[variable]

    values = df[variable].to_numpy()
    dates = df["date"]

    # DCT high-pass filtering
    fourier_signal = dct(values, type=1, norm="forward")

    filtered_signal = fourier_signal.copy()
    filtered_signal[:cutoff] = 0

    satv = idct(filtered_signal, type=1, norm="forward")

    # Robust control limits
    median_satv = np.median(satv)
    mad = np.median(np.abs(satv - median_satv))
    robust_std = 1.4826 * mad

    lower_bound = median_satv - n_std * robust_std
    upper_bound = median_satv + n_std * robust_std

    upper_outliers = satv > upper_bound
    lower_outliers = satv < lower_bound
    outliers = upper_outliers | lower_outliers

    baseline = values - satv

    lower_curve = baseline + lower_bound
    upper_curve = baseline + upper_bound

    # Interactive Plotly figure
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode="lines",
        name=f"Average {name.lower()}"
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=lower_curve,
        mode="lines",
        name="Lower SPC boundary",
        line=dict(dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=dates,
        y=upper_curve,
        mode="lines",
        name="Upper SPC boundary",
        line=dict(dash="dash")
    ))

    fig.add_trace(go.Scatter(
        x=dates[outliers],
        y=values[outliers],
        mode="markers",
        name="Outliers",
        marker=dict(color="red", size=5)
    ))

    fig.update_layout(
        title=f"{name} — SATV and SPC",
        xaxis_title="Date",
        yaxis_title=f"{name} ({unit})",
        height=500
    )

    summary = {
        "total_observations": len(values),
        "total_outliers": int(outliers.sum()),
        "upper_outliers": int(upper_outliers.sum()),
        "lower_outliers": int(lower_outliers.sum()),
        "outlier_percentage": round(100 * outliers.mean(), 2),
        "median_satv": float(median_satv),
        "robust_std": float(robust_std)
    }

    return fig, summary

def weather_lof(df, variable="temperature_2m", contamination=0.01):

    name, unit = WEATHER_PROPERTIES[variable]

    values = df[variable].to_numpy()
    dates = df["date"]

    X = values.reshape(-1, 1)

    lof = LocalOutlierFactor(
        n_neighbors=min(20, len(values) - 1),
        contamination=contamination
    )

    labels = lof.fit_predict(X)

    anomalies = labels == -1

    # Interactive Plotly figure
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=values,
        mode="lines",
        name=f"Average {name.lower()}"
    ))

    fig.add_trace(go.Scatter(
        x=dates[anomalies],
        y=values[anomalies],
        mode="markers",
        name="LOF anomalies",
        marker=dict(color="red", size=5)
    ))

    fig.update_layout(
        title=f"{name} anomalies (LOF)",
        xaxis_title="Date",
        yaxis_title=f"{name} ({unit})",
        height=500
    )

    summary = {
        "total_observations": len(values),
        "total_anomalies": int(anomalies.sum()),
        "anomaly_percentage": round(100 * anomalies.mean(), 2),
        "mean_value": float(np.mean(values)),
        "mean_anomaly_value": float(np.mean(values[anomalies]))
            if anomalies.any() else None,
        "min_anomaly_value": float(np.min(values[anomalies]))
            if anomalies.any() else None,
        "max_anomaly_value": float(np.max(values[anomalies]))
            if anomalies.any() else None
    }

    return fig, summary

def sliding_window_correlation(
    df,
    weather_variable,
    window=12,
    lag=0
):
    x = df[weather_variable].shift(lag)
    y = df["fill_level_change"]

    swc = y.rolling(window, center=True).corr(x)

    return swc

def plot_swc(swc, weather_variable, window=12, lag=0):

    name, unit = WEATHER_PROPERTIES[weather_variable]

    fig = px.line(
        x=swc.index,
        y=swc.values,
        title=f"SWC – {name} | Window: {window} weeks | Lag: {lag} weeks",
        labels={
            "x": "Date",
            "y": "Correlation"
        }
    )

    fig.update_traces(line=dict(color="blue"))
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_yaxes(range=[-1, 1])
    fig.update_layout(height=450)

    return fig