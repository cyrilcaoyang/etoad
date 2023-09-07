import numpy as np
from scipy import signal, optimize


def smoothness_score(
        window_size: int,
        polyorder: int,
        column: np.array    # a 1D numpy array
) -> float:
    """
    Define a function that calculates a smoothness score
    Calculates a smoothness score for a given window size and data.
    We use the sum of squared differences from the original data to the smoothed data as the score.
    """
    smoothed_data = signal.savgol_filter(column, window_size, polyorder)
    score = np.sum((smoothed_data - column)**2)
    return score


def opt_window_size(
        polyorder: int,
        column: np.array,   # a 1D numpy array
) -> int:
    """
    Define a function to minimize the smoothness score
    """
    objective = lambda window_size: smoothness_score(int(window_size), polyorder, column)
    result = optimize.minimize_scalar(
        objective, bounds=(3, len(column)-1), method='bounded'
    )
    return int(result.x)


def smooth(
        column_num: int,
        data: list,     # a list of 2D numpy arrays
        polyorder: int = 3
) -> np.array:
    """
    Smooths the data by applying a Savitzky-Golay filter.

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
        for row_idx, row in enumerate(data[i]):
            column = row[:, column_num]
            window_size: int = opt_window_size(polyorder, column)
            new_column = signal.savgol_filter(column, window_size, polyorder)
            new_data[i][row_idx][:, column_num] = new_column
    return new_data

