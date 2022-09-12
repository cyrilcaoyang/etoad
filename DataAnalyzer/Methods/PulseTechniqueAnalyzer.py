from typing import List
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

from .EChemDataAnalyzer import EChemDataAnalyzer
from ..AnalysisUtils import rubberband_baseline_removal, estimate_noise, filter_peaks, select_peaks
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

    def __init__(self, *args):
        super().__init__(*args)
        self._separate_iterations()

    @staticmethod
    def _process_reduction_data(
            reduction_data: np.ndarray
    ) -> np.ndarray:
        """
        Processes the reduction data by
            - sorting the voltages from negative to positive
            - taking the absolute value of the currents
        to account for a possible pos -> neg scanning direction.

        Args:
            reduction_data: One iteration from the Multi-SWV data which voltage sweeps from high to low.

        Return:
            reduction_data: reduction_data overwrote following roles state above
        """
        idx_sorted: np.ndarray = np.argsort(reduction_data[:, 1])
        reduction_data = reduction_data[idx_sorted, :]
        reduction_data[:, 2] = abs(reduction_data[:, 2])
        return reduction_data

    @staticmethod
    def _classify_oxidation_reduction(
            data_of_iteration: np.ndarray
    ) -> dict:
        """
        Classify each iteration of Multi_SWV data as oxidation/reduction.
        Change ndarry to dictionary of ndarry. Key is oxidation/reduction.
        Value is data from each iteration.

        Args:
            data_of_iteration: One iteration from Multi-SWV raw data.
        """
        if data_of_iteration[:,1][0] < data_of_iteration[:,1][-1]:
            return {"oxidation":data_of_iteration}
        else:
            return {"reduction":data_of_iteration}

    def _separate_iterations(
            self
    ) -> None:
        """
        Separates the processed Multi-SWV data into a dictionary of a dictionary of ndarry.
        The first key is "iteration_number". The second key is "oxidation" or "reduction".
        The ndarray represents one SWV iteration.
        Overrides self._raw_data.
        """
        no_iterations = int(np.max(self._raw_data[:,3])+1)
        self._raw_data = {f"iteration_{iteration}": self._raw_data[self._raw_data[:,3] == iteration] for iteration in range(no_iterations)}
        for iteration in self._raw_data.keys():
            self._raw_data[iteration] = self._classify_oxidation_reduction(self._raw_data[iteration])
            self._analysis_results[iteration] = {}

    def _set_methods(self):
        """
        Implementation of the abstract method.
        Sets the self._analysis_methods attribute as the factory pattern.
        """
        self._analysis_methods = {
            "Peak Picking": self._peak_picking,
            #"CV Parameters": self._get_cv_parameters,
            "Plot": self._plot
        }

    def _peak_picking(
            self,
            min_peak_width: float,
            min_signal_noise: float,
            rel_height: float,
            **kwargs
    ) -> None:
        """
        Performs peak picking based on the raw data.
        Peak picking height threshold is determined by 5*signal/noise (estimated as 5*baseline).

        Writes the peak list (each peak as a dictionary) into self._analysis_results.

        Args:
             min_peak_width: Minimum width of a peak to be considered.
             min_height_baseline: Minimum height of a peak (relative to the baseline)
             rel_height: Relative height (from the top) to determine onset / offset and peak width.
        """
        for iteration in self._raw_data.keys():
            redox_process: str = list(self._raw_data[iteration].keys())[0]
            data_of_iteration = self._raw_data[iteration][redox_process]
            peak_selection_parms = {
                "data_of_iteration": data_of_iteration,
                "iteration": iteration,
                "min_peak_width": min_peak_width,
                "min_signal_noise": min_signal_noise,
                "rel_height": rel_height,
                "redox_process": redox_process
            }

            if redox_process == "reduction":
                data_of_iteration = self._process_reduction_data(
                    reduction_data=data_of_iteration
                )
            self._pick_peaks(**peak_selection_parms)



    def _pick_peaks(
            self,
            data_of_iteration: np.ndarray,
            iteration: str,
            min_peak_width: float,
            min_signal_noise: float,
            rel_height: float,
            redox_process: str,
            **kwargs
    ) -> None:
        """
        Pick peaks from the data and assign it to _analysis_result dictionary

        Args:
            data_of_iteration: One iteration from Multi-SWV raw data.
            iteration: A string states which iteration the data is.
            min_peak_width: Minimum width of a peak to be considered.
            min_height_baseline: Minimum height of a peak (relative to the baseline)
            rel_height: Relative height (from the top) to determine onset / offset and peak width.
            redox_process: "Oxidation" or "Reduction"
        """
        currents_corrected: np.ndarray = rubberband_baseline_removal(
            data_of_iteration[:, 1],
            data_of_iteration[:, 2]
        )

        noise: float = estimate_noise(
            data=currents_corrected,
            min_peak_width=min_peak_width
        )

        peaks_picked, peak_properties = find_peaks(
            currents_corrected,
            height=min_signal_noise*noise,
            width=min_peak_width,
            rel_height=rel_height
        )

        self._analysis_results[iteration]["Peak Picking"] = self._get_peak_data(data_of_iteration,peaks_picked, peak_properties,redox_process)

    @staticmethod
    def _get_peak_data(
            data_of_iteration: np.ndarray,
            peaks_picked: np.ndarray,
            peak_properties: dict,
            redox_process: str
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

        if not peaks_picked.any():
            return peaks

        max_shape_factor = max([peak_properties["peak_heights"][i] / peak_properties["widths"][i] for i in range(len(peaks_picked))])

        for i, peak_idx in enumerate(peaks_picked):
            onset_idx = int(peak_properties["left_ips"][i])
            offset_idx = int(peak_properties["right_ips"][i])
            height = -peak_properties["peak_heights"][i] if redox_process == "reduction" else peak_properties["peak_heights"][i]
            peaks.append(
                {
                    "onset": data_of_iteration[onset_idx, 1],
                    "offset": data_of_iteration[offset_idx, 1],
                    "peak": data_of_iteration[peak_idx, 1],
                    "onset_idx": onset_idx,
                    "peak_idx": peak_idx,
                    "offset_idx": offset_idx,
                    "height": height,
                    "width": peak_properties["widths"][i],
                    "shape_factor": peak_properties["peak_heights"][i] / peak_properties["widths"][i],
                    "rel_shape_factor": peak_properties["peak_heights"][i] / peak_properties["widths"][i] / max_shape_factor,
                    "overlap": False
                }
            )

        # Compares offset of peak i and onset of peak i+1 for peak overlap.
        # TODO: Check if this can be efficiently done with np.diff?
        for peak1, peak2 in zip(peaks, peaks[1:]):
            if peak1["offset"] > peak2["onset"]:
                peak1["overlap"] = True
                peak2["overlap"] = True
                peak2["offset"] = peak1["offset"]
                peak1["offset"] = peak2["onset"]

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
        #TODO: ReImplement this function to match the new data structure of the _raw_data
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
        data_all_iterations: list = []
        for iteration in self._raw_data.keys():
            data_all_iterations.append(self._raw_data[iteration].get(list(self._raw_data[iteration].keys())[0]))
        figure = DataVisualizer.plot_multiple_curves(
            data_to_plot=[(iteration[:, 1], iteration[:, 2]) for iteration in data_all_iterations],
            x_label="Voltage / V",
            y_label="Current / A",
            title=title,
            legend=[f"Iteration {i}" for i in range(1, len(data_all_iterations) + 1)]
        )

        self._figures[self.analysis_method_name] = figure
