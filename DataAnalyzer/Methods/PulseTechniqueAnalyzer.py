from typing import List
import numpy as np
from scipy.signal import find_peaks

from .EChemDataAnalyzer import EChemDataAnalyzer
from ..AnalysisUtils import als_baseline_detection, filter_peaks, select_peaks
from ..AnalysisUtils import DataVisualizer


class PulseTechniqueAnalyzer(EChemDataAnalyzer):
    """
    Implementation of the EChemDataAnalyzer for pulsed electrochemical techniques
    (e.g. Square Wave Voltammetry, Differential Pulse Voltammetry).

    Available analysis techniques:
        "Peak Picking" -> selects and characterizes peaks
        "CV Parameters" -> infers CV voltage range based on pre-defined selection criteria
        "Plot" -> plots the voltammogram
    """
    analysis_method_name: str = "PulsedTechniques"

    def _set_methods(self):
        """
        Implementation of the abstract method.
        Sets the self._analysis_methods attribute as the factory pattern.
        """
        self._analysis_methods = {
            "Peak Picking": self._peak_picking,
            "CV Parameters": self._get_cv_parameters,
            "Plot": self._plot
        }

    def _peak_picking(
            self,
            baseline_smoothing: float,
            baseline_weighting: float,
            min_peak_width: float,
            rel_height: float,
            **kwargs
    ) -> None:
        """
        Performs peak picking based on the raw data.
        Peak picking height threshold is determined by 5*signal/noise (estimated as 5*baseline).

        Writes the peak list (each peak as a dictionary) into self._analysis_results.

        Args:
             baseline_smoothing: Smoothing parameter for the baseline fitting (default approx. 1E7).
             baseline_weighting: Parameter for weighting deviations from the baseline (default approx. 1E-2).
             min_peak_width: Minimum width of a peak to be considered.
             rel_height: Relative height (from the top) to determine onset / offset and peak width.
        """
        baseline: np.ndarray = als_baseline_detection(
            self._raw_data[:, 2],
            smoothing=baseline_smoothing,
            weighting=baseline_weighting
        )

        peaks_picked, peak_properties = find_peaks(
            self._raw_data[:, 2],
            height=5*baseline,
            width=min_peak_width,
            rel_height=rel_height
        )

        self._analysis_results["Peak Picking"] = self._get_peak_data(peaks_picked, peak_properties)

    def _get_peak_data(
            self,
            peaks_picked: np.ndarray,
            peak_properties: dict
    ) -> List[dict]:
        """
        Extracts metadata about each peak from the peak picking results (from scipy.find_peaks).

        Args:
            peaks_picked: List of indices of peak maxima.
            peak_properties: Dictionary of extracted peak properties

        Returns:
            peaks: List of dictionaries of peak metadata (onset, max, offset, overlap)
        """
        peaks: list = []

        for i, peak_idx in enumerate(peaks_picked):

            onset_idx = int(peak_properties["left_ips"][i])
            offset_idx = int(peak_properties["right_ips"][i])

            peaks.append(
                {
                    "onset": self._raw_data[onset_idx, 1],
                    "offset": self._raw_data[offset_idx, 1],
                    "peak": self._raw_data[peak_idx, 1],
                    "onset_idx": onset_idx,
                    "peak_idx": peak_idx,
                    "offset_idx": offset_idx,
                    "height": peak_properties["peak_heights"][i],
                    "overlap": False
                }
            )

        # Compares offset of peak i and onset of peak i+1 for peak overlap.
        # TODO: Check if this can be efficiently done with np.diff?
        for peak1, peak2 in zip(peaks, peaks[1:]):
            if peak1["offset"] > peak2["onset"]:
                peak1["overlap"] = True
                peak2["overlap"] = True

        return peaks

    def _get_cv_parameters(
            self,
            filters: List[dict],
            selection: dict,
            min_voltage: float,
            max_voltage: float,
            additional_voltage: float,
            **kwargs
    ) -> None:
        """
        Selects the desired peak from the peak picking results for CV analysis.
        Filters the peaks (applying filter operations), then selects the specified peak from the filtered peak list.

        Writes the CV parameters with the 'Voltage Profile' parameter adjusted into self._analysis_results.

        Args:
             filters: List of filters (structure see filter_peaks documentation) for filtering the picked peaks.
             selection: Selection criterion (structure see select_peaks documentation).
             max_voltage: Maximum voltage allowed for CV measurements.
             min_voltage: Minimum voltage allowed for CV measurements.
             additional_voltage: Voltage range beyond the peak onset/offset to be scanned.
        """

        try:
            filtered_peaks: list = filter_peaks(self._analysis_results["Peak Picking"], filters)
            selected_peak_idx, selected_peak = select_peaks(filtered_peaks, selection)
        except (TypeError, ValueError):
            self._analysis_results["CV Parameters"] = "SKIP"
            return

        # determine onset and offset of previous / next peak to determine cv boundaries
        for peak in self._analysis_results["Peak Picking"]:
            if peak["peak"] < selected_peak["peak"]:
                min_voltage = peak["offset"]
            elif peak["peak"] > selected_peak["peak"]:
                max_voltage = peak["onset"]

        min_voltage = float(max(min_voltage, selected_peak["onset"] - additional_voltage))
        max_voltage = float(min(max_voltage, selected_peak["offset"] + additional_voltage))

        self._analysis_results["CV Parameters"] = [max_voltage, max_voltage, min_voltage, max_voltage, max_voltage]
        # TODO: implement logging, warnings (e.g. for overlapping peaks), STOP and SKIP keywords

    def _plot(
            self,
            title: str,
            **kwargs
    ) -> None:
        """
        Plots the raw data by creating a figure object, saves the figure object to self._figures.

        Args:
            title: Title of the plot
        """
        figure = DataVisualizer.plot_single_curve(
            x_values=self._raw_data[:, 1],
            y_values=self._raw_data[:, 2],
            x_label="Voltage / V",
            y_label="Current / A",
            title=title,
        )

        self._figures[self.analysis_method_name] = figure
