import numpy as np
import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from statsmodels.tsa.seasonal import STL
from scipy.signal import stft


def reservoir_stl(fill_level, seasonal=13, trend=105, robust=True, area="NO"):
    """
    Decompose weekly reservoir filling levels using STL.

    Returns an interactive Plotly figure and the STL result.
    """

    stl = STL(
        fill_level,
        period=52,
        seasonal=seasonal,
        trend=trend,
        robust=robust
    )

    result = stl.fit()

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=[
            "Observed fill level",
            "Trend",
            "Seasonal component",
            "Residual component"
        ]
    )

    components = [
        (fill_level, "Observed", "#38BDF8"),
        (result.trend, "Trend", "#F59E0B"),
        (result.seasonal, "Seasonal", "#22C55E"),
        (result.resid, "Residual", "#F87171")
    ]

    for row, (values, name, colour) in enumerate(components, start=1):

        fig.add_trace(
            go.Scatter(
                x=fill_level.index,
                y=values,
                mode="lines",
                name=name,
                line=dict(color=colour),
                hovertemplate="%{y:.2%}<extra></extra>"
            ),
            row=row,
            col=1
        )

        fig.update_yaxes(
            tickformat=".0%",
            row=row,
            col=1
        )

    fig.update_layout(
        title=f"STL Decomposition — {area}",
        height=850,
        showlegend=False,
        hovermode="x unified"
    )

    fig.update_xaxes(title_text="Date", row=4, col=1)

    return fig, result


def reservoir_spectrogram(fill_level, nperseg=208, noverlap=104, area="NO"):
    """
    Create an interactive spectrogram of weekly reservoir filling levels.

    Returns the Plotly figure and STFT results.
    """

    y = fill_level.to_numpy()

    y_centered = y - np.mean(y)

    f, t, Zxx = stft(
        y_centered,
        fs=1,
        nperseg=nperseg,
        noverlap=noverlap
    )

    # Convert weeks from start into calendar dates
    spectrogram_dates = (
        fill_level.index[0] +
        pd.to_timedelta(t * 7, unit="D")
    )

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.10,
        subplot_titles=[
            f"{area} Reservoir Filling Levels",
            "Spectrogram"
        ],
        row_heights=[0.4, 0.6]
    )

    fig.add_trace(
        go.Scatter(
            x=fill_level.index,
            y=y,
            mode="lines",
            name="Fill level",
            line=dict(color="#38BDF8"),
            hovertemplate="%{y:.2%}<extra></extra>"
        ),
        row=1,
        col=1
    )

    fig.add_trace(
        go.Heatmap(
            x=spectrogram_dates,
            y=f,
            z=np.abs(Zxx),
            colorscale="Viridis",
            colorbar=dict(
                title="Magnitude",
                len=0.5,
                y=0.25
            ),
            hovertemplate=(
                "Date: %{x|%Y-%m-%d}<br>"
                "Frequency: %{y:.4f} cycles/week<br>"
                "Magnitude: %{z:.4f}"
                "<extra></extra>"
            )
        ),
        row=2,
        col=1
    )

    fig.update_yaxes(
        title_text="Fill level",
        tickformat=".0%",
        row=1,
        col=1
    )

    fig.update_yaxes(
        title_text="Frequency (cycles/week)",
        range=[0, 0.08],
        row=2,
        col=1
    )

    fig.update_xaxes(
        title_text="Date",
        row=2,
        col=1
    )

    fig.update_layout(
        height=700,
        showlegend=False
    )

    return fig, (f, t, Zxx)