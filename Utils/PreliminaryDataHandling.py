import pickle
from pathlib import Path
from typing import Any, Union

import matplotlib.pyplot as plt
import numpy as np


def save_data(
        object_to_save: Any,
        file_name: Path
) -> None:
    """
    Saves the passed Python object into a pickle file.

    Args:
        object_to_save: Object to be saved (any type).
        file_name: Path to the file where the pkl file should be stored.
    """
    with open(file_name, "wb") as pklfile:
        pickle.dump(object_to_save, pklfile)


def scatter_plot(
        x_values: np.array,
        y_values: np.array,
        save: bool = False,
        file_name: Union[Path, None] = None
) -> None:
    """
    Crude matplotlib scatter plot to visualize the results and see if the measurement was somewhat successful.

    Args:
        x_values: Numpy array of the x values of all data points
        y_values: Numpy array of the y values of all data points
        save: Boolean whether the scatter plot should be saved or not.
        file_name: Path to the file where the scatter plot should be saved.
    """
    plt.scatter(x_values, y_values)
    plt.show()

    if save:
        plt.savefig(file_name)
