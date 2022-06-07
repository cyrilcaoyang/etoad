from typing import Optional, Callable
import numpy as np
from .EChemMethod import EChemMethod


class SWV(EChemMethod):
    """
    Implementation of the Square Wave Voltammetry Method.
    """
    method_file_name: str = "swv4.ecc"
    data_structure: tuple = ("Time", "Voltage", "Current")

    @staticmethod
    def _decode_row(row: tuple, timebase: float, numeric_to_single: Optional[Callable]) -> np.array:
        """
        SWV-Specific implementation of decoding a single row of experimental results:

        Args:
            row: Tuple of values parsed from the experimental data
            timebase: Current time base step, as extracted from the metadata.
            numeric_to_single: Function to convert C++ signature numericals to singles.
        """
        time_high, time_low, voltage, current = row

        time = timebase * ((time_high << 32) + time_low)
        current = numeric_to_single(current)
        voltage = numeric_to_single(voltage)

        return np.asarray([time, voltage, current])
