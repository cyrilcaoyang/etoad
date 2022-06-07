from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional, Callable, Tuple
import numpy as np
from ..BioLogic import TECH_ID, PROG_STATE


class EChemMethod(metaclass=ABCMeta):

    method_file_name: str = ""
    data_structure: tuple = ()

    """
    Abstract base class for electrochemical methods to be run on the Bio-Logic Instrument using the Python Interface.
    """

    def __init__(self, path_to_binaries: Path):
        self.method = path_to_binaries / self.method_file_name

    def method_file(self) -> str:
        return str(self.method)

    # TODO: implement parameter parsing and take that away from the API

    @classmethod
    def decode_data(cls, data: tuple, numeric_to_single: Optional[Callable]) -> Tuple[np.ndarray, dict]:
        """
        Abstract method to decode the experimentally recorded data into a numpy ndarray.

        Args:
            data: Tuple of data recorded from the API  # TODO: figure out and type-hint properly
            numeric_to_single: Function that can convert a numeric value to a 32-bit value (from the API).

        Returns:
            extracted_data: Numpy ndarray of all experimental data extracted.
            metadata: Dictionary of experiment metadata.
        """
        current_values, data_info, data_record = data
        metadata = cls._unpack_metadata(current_values, data_info)
        extracted_data: np.ndarray = np.array([])

        start_index = 0
        for _ in range(data_info.NbRows):
            row: tuple = data_record[start_index: start_index + data_info.NbCols]
            extracted_row: np.array = cls._decode_row(row, metadata["timebase"], numeric_to_single)
            extracted_data = cls.merge_data(extracted_data, extracted_row)
            start_index = start_index + data_info.NbCols

        return extracted_data, metadata

    @staticmethod
    def _unpack_metadata(current_values, data_info) -> dict:
        """
        Extracts the metadata from the experimentally recorded data.

        Args:
            current_values:
            data_info:  # TODO: figure out and type-hint properly

        Returns:
            # TODO: type-hint and document properly by debugging data that is returned from the experiment
        """
        status = PROG_STATE(current_values.State).name
        technique_name = TECH_ID(data_info.TechniqueID).name

        metadata = {
            "timebase": current_values.TimeBase,
            "index": data_info.TechniqueIndex,
            "technique": technique_name,
            "process_index": data_info.ProcessIndex,
            "loop": data_info.loop,
            "skip": data_info.IRQskipped,
            "status": status
        }

        return metadata

    @staticmethod
    @abstractmethod
    def _decode_row(row: tuple, timebase: float, numeric_to_single: Optional[Callable]) -> np.array:
        """
        Method to decode a single row of experimental data recorded experimentally.

        Args:
            row: Tuple of values as extracted from output of the DLL functions.
            timebase: Current time base step, as extracted from the metadata
            numeric_to_single: Function that can convert a numeric value to a 32-bit value (from the API).
        """
        # TODO: figure out if it is possible to write a general decoder based on class properties only
        # TODO: might need to be converted to classmethod then
        pass

    @staticmethod
    def merge_data(original_data: np.ndarray, new_data: np.array) -> np.ndarray:
        """
        Merges a new 1D numpy array (new_data) into a 2D array (original_data) by appending it along axis 0.
        If the original_data array is empty, a new 2D array of correct dimensionality is generated from new_data.

        Args:
            original_data: 2D Numpy ndarray
            new_data: 1D Numpy array to be appended to original_data

        Returns:
            2D Numpy array as a merger from original_data and new_data.
        """
        if original_data.size != 0:
            return np.append(original_data, [new_data], axis=0)
        else:
            return np.array([new_data])
