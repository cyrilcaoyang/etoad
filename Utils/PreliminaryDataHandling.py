import pickle
from pathlib import Path
from typing import Any, Union

import matplotlib.pyplot as plt
import numpy as np


def save_as_pkl(
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


def save_as_csv(
        object_to_save: dict,
        file_name: Path
) -> None:
    """
    Saves a dictionary as a csv file.
    Possible dictionary formats:
        str: Union[str, int, float, bool]
        str: Union[List[Union[str, int, float, bool]], Tuple[Union[str, int, float, bool]]]

    Args:
        object_to_save: Dictionary of the abovementioned format
        file_name: Path to the file where the csv file should be stored.
    """
    with open(file_name, "w") as csv_file:
        for key, value in zip(object_to_save.keys(), object_to_save.values()):
            if isinstance(value, (str, int, float, bool)):
                csv_file.write(f"{key},{value}\n")
            elif isinstance(value, (list, tuple)):
                csv_file.write(f"{key},{','.join(value)}\n")


def scatter_plot(
        x_values: np.array,
        y_values: np.array,
        show: bool = True,
        save: bool = False,
        file_name: Union[Path, None] = None
) -> None:
    """
    Crude matplotlib scatter plot to visualize the results and see if the measurement was somewhat successful.

    Args:
        x_values: Numpy array of the x values of all data points
        y_values: Numpy array of the y values of all data points
        show: Boolean whether the scatter plot should be shown or not.
        save: Boolean whether the scatter plot should be saved or not.
        file_name: Path to the file where the scatter plot should be saved.
    """
    plt.scatter(x_values, y_values)

    if show:
        plt.show()

    if save:
        plt.savefig(file_name)

    plt.close()
