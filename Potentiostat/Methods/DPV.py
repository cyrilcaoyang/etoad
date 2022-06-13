from typing import Optional, Callable
import numpy as np
from .EChemMethod import EChemMethod


class DPV(EChemMethod):
    """
    Implementation of the Square Wave Voltammetry Method.
    """
    method_file_name: str = "dpv4.ecc"
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

    def process_data(self, extracted_data: np.ndarray) -> np.ndarray:
        """
        TODO: Document properly
        Generates the differential CV spectrum from the pulsed technique
        """
        processed_data: np.ndarray = np.array([])

        # TODO: Write this loop in a more numpy fashion, just a quick & dirty implementation now
        for i in range(0, len(extracted_data), 2):
            differential_current: float = extracted_data[i+1, 2] - extracted_data[i, 2]
            processed_data = self._merge_data(processed_data, np.asarray([extracted_data[i, 0], extracted_data[i, 1], differential_current]))

        return processed_data