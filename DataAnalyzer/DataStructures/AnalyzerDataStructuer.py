__author__ = 'Yunheng(Jackie) Zou'

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple


class ScatterCurve(object):
    """A data type to handle 2d point based signal (must be a function form)
    by connecting two dots with straight line"""

    def __init__(self,
                 data: np.ndarray,
                 column_x_index: int,
                 column_y_index: int):
        """
        Args:
            data: numpy array, each row stand for one set of data, each column stand for one type of data,
            just like an excel table
            column_x_index: specify index for the type of data as x
            column_y_index: specify index for the type of data as y
        """
        self.data = np.hstack((data[:, [column_x_index]], data[:, [column_y_index]]))

    def y_predictor(self, x: float) -> float:

        # ATTN: Is this linear interpolation between two data points?
        # ATTN: a) This has a problem once you have a non-monotonic sequence of data points (e.g. two CV cycles)
        # ATTN: b) Numpy already has a (better + more efficient) solution to this -> numpy.interp()

        """

        Args:
            x: float value of x coordinate

        Returns: estimated y coordinate value correspond to x coordinate

        """
        difference = np.abs((x - self.data[:, 0]))
        sorted_difference = np.sort(difference)
        min_diff = sorted_difference[0]
        sec_min_diff = sorted_difference[1]
        index_min: int = np.where(difference == min_diff)[0][0]
        index_sec_min: int = np.where(difference == sec_min_diff)[0][0]
        point1 = self.data[index_min, :]
        point2 = self.data[index_sec_min, :]
        y: int = (point2[1] - point1[1]) / (point2[0] - point1[0]) * (x - point1[0]) + point1[1]
        return y

    def integral_operator(self) -> float:

        # ATTN: Numpy has a faster and more accurate solution for this: numpy.trapz()

        """

        Returns:
            integral: the integral of the curve as a float using approximation with 2000 step

        """
        min_x: float = np.min(self.data[:, 0])
        max_x: float = np.max(self.data[:, 0])
        steps: int = 2000  # default settings todo: smart steps estimation to minimize errors
        increment: float = (max_x - min_x) / steps
        x_ticks: np.ndarray = np.arange(min_x, max_x, increment)
        y_ticks: np.ndarray = np.array([self.y_predictor(xi) for xi in x_ticks])
        # plt.scatter(x_ticks,y_ticks)
        # plt.show()
        integral: float = np.sum(increment * y_ticks[:-1])
        return integral

    def first_derivative(self) -> np.ndarray:

        # ATTN: Numpy has a more accurate and efficient solution to this: numpy.gradient()

        """
        Assign first derivative of the selected data
        Returns:
            gradient
        """
        voltage = self.data[:, 0].flatten()
        current = self.data[:, 1].flatten()
        delta_voltage = (voltage[:-1] - voltage[1:])
        delta_current = (current[:-1] - current[1:])
        first_derivative: np.ndarray = delta_current / delta_voltage
        return first_derivative

    def first_derivative_peak_detection(self) -> Tuple[list, list]:

        # ATTN: This only works for determining zero crossings with negative second derivative.
        # ATTN: There are probably more efficient ways to do this, maybe check something like this:
        # https://python.tutorialink.com/efficiently-detect-sign-changes-in-python/

        """
        Find the row index of peak inside the data
        Args:
            first_derivative_array: first derivative of current data

        Returns:
            upper_peak: list of local maximum index
            lower_peak: list of local minimum index
        """
        first_derivative_array = self.first_derivative()
        upper_peak = list()
        lower_peak = list() #todo: delete lower peak not necessary
        for i in range(1, first_derivative_array.size):  # ATTN: Iteration is always slow :-)
            if first_derivative_array[i] < 0 < first_derivative_array[i - 1]:
                upper_peak.append(i)
        return upper_peak, lower_peak
