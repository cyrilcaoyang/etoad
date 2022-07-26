import pickle
from pathlib import Path
from typing import Any


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
