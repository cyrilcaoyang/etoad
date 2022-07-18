__author__ = 'Yunheng(Jackie) Zou'

import numpy as np
import copy
from ..DataStructures import ScatterCurve
from typing import Tuple

# ATTN: We could discuss the use of abstract base classes as class prototypes at some point (similar to the EChemMethod.py)
#  That would also include some further inheritance rather than re-coding certain methods.


class CVAnalyzer(object):

    def __init__(self, data):
        self.data = data

    def _forward_backward_gradient(self, array) -> np.ndarray:
        """
        Adding additional column for - dV/dt gradient
        Returns:
            array: the data array with additional gradient column
        """
        voltage = array[:, 1].flatten()
        voltage_t_minus1 = np.zeros(voltage.size)
        voltage_t_minus1[1:] = voltage[:-1]
        gradient = (voltage_t_minus1 - voltage).reshape((-1, 1))
        array = np.hstack((array, gradient))
        return array

    def _acquire_cycle_num(self) -> int:
        """
        Acquire number of cycle in CV measurement
        Note: cycle number start at 0
        Returns:
                Cycle number
        """
        cycle_num = int(np.max(self.data[:, 3]))
        return cycle_num

    def _acquire_data_at_cycle_n(self, cycle_num: int):
        data = self.data
        cycle_n_data: np.ndarray = data[data[:, 3] == cycle_num]
        return cycle_n_data

    def analysis(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create recording for integral per cycle;
        Create recording for peak per cycle ;
        Store all these in 2 seperate numpy array.
        Returns:
            integral_data_ary: cycle number vs integral
            peak_data_ary: every single peak information
            [[ cycle, peak voltage, peak current]
             [ cycle, peak voltage, peak current]]
        """
        # TODO: make this method better readable and understandable
        #  probably break down into several sub-routines

        total_cycle_nums: int = self._acquire_cycle_num() + 1  # ATTN: It might make more sense to pass the number of cycles than to infer it from the data
        integral_data = list()  # todo: refactor
        peak_data = list()
        for cycle_num in range(total_cycle_nums):
            cycle_data: np.ndarray = self._acquire_data_at_cycle_n(cycle_num)
            cycle_data = self._forward_backward_gradient(cycle_data)
            upper_cycle: np.ndarray = cycle_data[cycle_data[:, 4] < 0]
            lower_cycle: np.ndarray = cycle_data[cycle_data[:, 4] > 0]
            upper_scatter = ScatterCurve(upper_cycle, 1, 2)
            lower_scatter = ScatterCurve(lower_cycle, 1, 2)
            # finding integral
            upper_integral = upper_scatter.integral_operator()
            lower_integral = lower_scatter.integral_operator()
            total_area = upper_integral - lower_integral
            integral_data.append([cycle_num, total_area])
            # finding peaks
            upper_peaks: Tuple[list, list] = upper_scatter.first_derivative_peak_detection()
            lower_peaks: Tuple[list, list] = lower_scatter.first_derivative_peak_detection()
            upper_local_maximum = upper_peaks[0]
            lower_local_minimum = lower_peaks[0]
            # store peak information
            for i in upper_local_maximum:
                peak_data.append([cycle_num, upper_scatter.data[i,:][0],upper_scatter.data[i,:][1]])
            for i in lower_local_minimum:
                peak_data.append([cycle_num, lower_scatter.data[i, :][0], lower_scatter.data[i, :][1]])
        integral_data_ary = np.array(integral_data)
        peak_data_ary = np.array(peak_data)
        return integral_data_ary, peak_data_ary
