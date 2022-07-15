__author__ = 'Yunheng(Jackie) Zou'

import numpy as np
import copy
from ..DataStructures import ScatterCurve
from typing import Tuple
import scipy.signal as sps

class Pulse_Analyzer(object):

    def __init__(self,data):
        self.data = data

    def peak_detection(self, data) -> list:
        """
        Provide all the peak index position in the data array using local maximum detection
        Args:
            data: pulse technique data
            [[time, voltage, current]
             [time, voltage, current]
             [time, voltage, current]]

        Returns: a list of peak index

        """
        peaks = list()
        current = data[:, 2].flatten()
        for i in range(1, current.size - 1):
            if current[i] > current[i - 1] and current[i] > current[i + 1]:
                peaks.append(i)
        return peaks

    def threshold_denoising(self,data) -> np.ndarray:
        """
        zero out all the current signal that is within the threshold current based on the maximum peak current
        Args:
            data: pulse technique data
            [[time, voltage, current]
             [time, voltage, current]
             [time, voltage, current]]

        Returns: same data format but current being threholded

        """
        copyarray = data.copy()
        current = copyarray[:, 2] * (copyarray[:, 2] > np.max(copyarray[:, 2] * 0.05))
        copyarray[:, 2] = current
        return copyarray

    def high_frequency_noise_filter(self,threshold):
        """
        Filter all the high frequency signal in the data ary to make it smooth

        Args:
            threshold: threshold frequency #Todo: explain in detail

        Returns:
            data: same data format but current column being reasigned to Fourier filtered version
        """
        data = self.data.copy()
        b, a = sps.butter(4, threshold, "low", analog=False)
        filt_res = sps.filtfilt(b, a, data[:, 2])
        data[:,2] = filt_res
        return data

    def DPV_analysis(self) -> np.ndarray:
        """
        Provide peak information of the data set

        Returns:
            peak_data_ary:
            [peak_voltage, peak_current]

        """
        peak_data = list()
        data = self.high_frequency_noise_filter(0.3)
        data_thres = self.threshold_denoising(data)
        peaks = self.peak_detection(data_thres)
        for index in peaks:
            peak_voltage = self.data[index][1]
            peak_current = self.data[index][2]
            peak_data.append([peak_voltage,peak_current])
        peak_data_ary = np.array(peak_data)
        return peak_data_ary

    def SWV_analysis(self) -> np.ndarray:
        """
        Provide peak information of the data set

        Returns:
            peak_data_ary:
            [peak_voltage, peak_current]

        """
        peak_data = list()
        data_thres = self.threshold_denoising(self.data)
        peaks = self.peak_detection(data_thres)
        for index in peaks:
            peak_voltage = self.data[index][1]
            peak_current = self.data[index][2]
            peak_data.append([peak_voltage, peak_current])
        peak_data_ary = np.array(peak_data)
        return peak_data_ary


