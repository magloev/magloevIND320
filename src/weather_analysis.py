import numpy as np
import matplotlib.pyplot as plt

from scipy.fft import dct, idct
from sklearn.neighbors import LocalOutlierFactor


def precipitation_spc(df, cutoff=30, n_std=3):
    """
    Detect precipitation outliers using DCT high-pass filtering
    and robust Statistical Process Control (SPC).

    Returns the plot and a summary of outliers.
    """

    precipitation = df["precipitation"].to_numpy()
    dates = df["date"]

    fourier_signal = dct(precipitation, type=1, norm="forward")

    filtered_signal = fourier_signal.copy()
    filtered_signal[:cutoff] = 0

    satv = idct(filtered_signal, type=1, norm="forward")

    median_satv = np.median(satv)
    mad = np.median(np.abs(satv - median_satv))
    robust_std = 1.4826 * mad

    lower_bound = median_satv - n_std * robust_std
    upper_bound = median_satv + n_std * robust_std

    upper_outliers = satv > upper_bound
    lower_outliers = satv < lower_bound
    outliers = upper_outliers | lower_outliers

    baseline = precipitation - satv

    lower_curve = baseline + lower_bound
    upper_curve = baseline + upper_bound

    fig, ax = plt.subplots(figsize=(13, 5))

    ax.plot(dates, precipitation, label="Average precipitation", alpha=0.7)
    ax.plot(dates, lower_curve, "--", label="Lower SPC boundary")
    ax.plot(dates, upper_curve, "--", label="Upper SPC boundary")

    ax.scatter(
        dates[outliers],
        precipitation[outliers],
        color="red",
        s=12,
        label="Outliers",
        zorder=3
    )

    ax.set_title("Precipitation SPC — NO3, 2024")
    ax.set_xlabel("Date")
    ax.set_ylabel("Precipitation (mm)")
    ax.legend()

    plt.tight_layout()

    summary = {
        "total_observations": len(precipitation),
        "total_outliers": int(outliers.sum()),
        "upper_outliers": int(upper_outliers.sum()),
        "lower_outliers": int(lower_outliers.sum()),
        "outlier_percentage": round(100 * outliers.mean(), 2),
        "median_satv": float(median_satv),
        "robust_std": float(robust_std)
    }

    return fig, summary


def temperature_lof(df, contamination=0.01):
    """
    Detect temperature anomalies using Local Outlier Factor (LOF).

    Returns the plot and a summary of detected anomalies.
    """

    temperature = df["temperature_2m"].to_numpy()
    dates = df["date"]

    X = temperature.reshape(-1, 1)

    lof = LocalOutlierFactor(
        n_neighbors=20,
        contamination=contamination
    )

    labels = lof.fit_predict(X)

    anomalies = labels == -1

    fig, ax = plt.subplots(figsize=(13, 5))

    ax.plot(
        dates,
        temperature,
        label="Average temperature",
        alpha=0.7
    )

    ax.scatter(
        dates[anomalies],
        temperature[anomalies],
        color="red",
        s=15,
        label="LOF anomalies",
        zorder=3
    )

    ax.set_title("Temperature anomalies (LOF) — NO3, 2024")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()

    plt.tight_layout()

    summary = {
        "total_observations": len(temperature),
        "total_anomalies": int(anomalies.sum()),
        "anomaly_percentage": round(100 * anomalies.mean(), 2),
        "mean_temperature": float(np.mean(temperature)),
        "mean_anomaly_temperature": float(np.mean(temperature[anomalies]))
            if anomalies.any() else None,
        "min_anomaly_temperature": float(np.min(temperature[anomalies]))
            if anomalies.any() else None,
        "max_anomaly_temperature": float(np.max(temperature[anomalies]))
            if anomalies.any() else None
    }

    return fig, summary