import numpy as np
from scipy import signal, optimize


def _smoothness_score(
        column: np.array,
        window_length: int,
        poly: int) -> float:
    """
    Define a function that calculates a smoothness score
    """
    smoothed_data = signal.savgol_filter(column, window_length, poly, mode='nearest')
    score = np.sum((smoothed_data - column) ** 2)
    return score


def _opt_window_length(
        column: np.array,
        poly: int
) -> int:
    """
    Define a function to minimize the smoothness score
    """
    objective = lambda window_length: _smoothness_score(column, int(window_length), poly)
    result = optimize.minimize_scalar(
        objective, bounds=(3, len(column) - 1), method='bounded'
    )
    return int(result.x)


def smooth(
        column_num: int,
        data: list,     # a list of 2D numpy arrays
        polyorder: int = 2
) -> np.array:
    """
    Smooths the data by applying a Savitzky-Golay filter.
    window_length is automatically determined by the smoothness score.
    Args:
        column_num: Column number of the data to be smoothed.
        data: Numpy array of the raw data.
        window_length: Length of the filter window (i.e. the number of coefficients).
        polyorder: Order of the polynomial used to fit the samples.

    Returns:
        np.array: Numpy array of the smoothed data.
    """
    new_data = np.copy(data)
    for i in range(len(data)):
        column = data[i][:, column_num]
        window_length: int = _opt_window_length(column, polyorder)
        new_column = signal.savgol_filter(column, window_length, polyorder, mode='nearest')
        new_data[i][:, column_num] = new_column
    return new_data
