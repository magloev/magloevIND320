import numpy as np
import matplotlib.pyplot as plt

from statsmodels.tsa.seasonal import STL
from scipy.signal import stft


def reservoir_stl(fill_level, seasonal=13, trend=105, robust=True, area="NO"):
    """
    Decompose weekly reservoir filling levels using STL.

    Returns the decomposition plot and the STL result.
    """

    stl = STL(
        fill_level,
        period=52,
        seasonal=seasonal,
        trend=trend,
        robust=robust
    )

    result = stl.fit()

    fig = result.plot()
    fig.set_size_inches(13, 8)
    fig.suptitle(f"STL Decomposition — {area} Reservoir Filling Levels")

    fig.tight_layout()

    return fig, result


def reservoir_spectrogram(fill_level, nperseg=208, noverlap=104, area="NO"):
    """
    Create a spectrogram of weekly reservoir filling levels.

    Returns the Matplotlib figure and STFT results.
    """

    y = fill_level.to_numpy()

    y_centered = y - np.mean(y)

    f, t, Zxx = stft(
        y_centered,
        fs=1,
        nperseg=nperseg,
        noverlap=noverlap
    )

    fig, axs = plt.subplots(2, 1, figsize=(13, 8))

    axs[0].plot(np.arange(len(y)), y)
    axs[0].set_title(f"{area} Reservoir Filling Levels")
    axs[0].set_ylabel("Fill level")

    pcm = axs[1].pcolormesh(
        t,
        f,
        np.abs(Zxx),
        shading="auto"
    )

    axs[1].set_title("Spectrogram")
    axs[1].set_xlabel("Time (weeks from start)")
    axs[1].set_ylabel("Frequency (cycles/week)")

    axs[1].set_ylim(0, 0.08)

    fig.colorbar(pcm, ax=axs[1], label="Magnitude")

    plt.tight_layout()

    return fig, (f, t, Zxx)