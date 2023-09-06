import math
from typing import List, Tuple
import numpy as np
import pandas as pd
import itertools
from .EChemDataAnalyzer import EChemDataAnalyzer
from ..AnalysisUtils import DataVisualizer
from ..AnalysisUtils import significant_digits
from ...Utils import log_exceptions


class CVAnalyzer(EChemDataAnalyzer):
    """
    Implementation of the EChemDataAnalyzer for cyclic voltammetry.

    Available analysis techniques:
        "Peak Picking" -> selects and characterizes peaks
        "Integration" -> determines the integral within each CV cycle
        "Plot" -> plots the voltammograms
    """
    analysis_method_name: str = "CV"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._raw_data = self._split_cycles(self._raw_data)

    @staticmethod
    def _split_cycles(
            data: List[np.ndarray]
    ) -> List[List[np.ndarray]]:
        """
        Splits the raw data for each iteration into the individual CV cycles.

        Args:
            data: List of numpy ndarrays of the raw data for each iteration.

        Returns:
            List[List[np.ndarray]]: List of lists of numpy ndarrays of the raw data for each CV cycle.
        """
        skip_cycles: int = 2  # TODO: figure out a more flexible way to include this

        data_separated: List[List[np.ndarray]] = []
        for idx, iteration in enumerate(data):
            no_cycles: int = int(np.max(iteration[:, 3]) + 1)
            data_separated.append([iteration[iteration[:, 3] == cycle] for cycle in range(skip_cycles, no_cycles)])

        return data_separated

    def _set_methods(
            self
    ):
        """
        Implementation of the abstract method.
        Sets the self._analysis_methods attribute as the factory pattern
        """
        self._analysis_methods = {
            "Peak Picking": self._peak_picking,
            "Integration": self._integration,
            "Peaks Scanrate": self._plot_peaks_scan_rate,
            "Currents Scanrate": self._plot_currents_scan_rate,
            "Plot": self._plot
        }

    @staticmethod
    def _get_half_cycles(
            cycle: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Separates the oxidation and reduction half cycles of a CV cycle based on the first discrete difference
        along the voltage axis.

        Args:
            cycle: Numpy ndarray of the full CV cycle

        Returns:
            reduction: Numpy ndarray of the reduction half cycle (decreasing voltage)
            oxidation: Numpy ndarray of the oxidation half cycle (increasing voltage)
        """
        reduction: np.ndarray = cycle[np.diff(cycle[:, 1], append=0) < 0]
        oxidation: np.ndarray = cycle[np.diff(cycle[:, 1], append=0) > 0]

        return reduction, oxidation

    @log_exceptions
    def _peak_picking(
            self,
            **kwargs
    ) -> None:
        """
        Performs peak picking for the raw CV data.
        Divides each CV cycle into oxidation and reduction half, and determines the maxima and minima, respectively.
        Stores all data in self._analysis_results.
        """
        for idx, iteration in enumerate(self._raw_data):
            peaks_per_iteration: list = []
            for cycle in iteration:
                reduction, oxidation = self._get_half_cycles(cycle)
                peaks: list = self._pick_peaks(reduction, maxima=False) + self._pick_peaks(oxidation, maxima=True)
                peaks_per_iteration.append(peaks)
            self._analysis_results[f"Iteration {idx}"]["Peak Picking"] = peaks_per_iteration

    @staticmethod
    def _get_scan_rate(raw_data: List[np.ndarray]) -> float:
        """
        Extracts the scan rate of a CV cycle from the raw data (takes the first cycle by default).
        # ATTN: This is a helper method -- in principle, we should be able to directly take the scan rate from the
                measurement parameters.
        Args:
            raw_data: Data of a CV measurement (list of one np.ndarray per CV cycle).

        Returns:
            scan_rate: The scan rate of this cycle in V/s
        """
        times = raw_data[0][:, 0]
        voltages = raw_data[0][:, 1]
        scan_rate = 2 * (np.max(voltages) - np.min(voltages)) / (np.max(times) - np.min(times))
        return scan_rate

    @staticmethod
    def _pick_peaks(
            half_cycle: np.ndarray,
            maxima=True
    ) -> List[dict]:
        """
        Picks the peaks within a half CV cycle based on zero crossings in the first derivative.
        Distinguishes maxima / minima by the second derivative at this point.

        Args:
            half_cycle: Raw data of the half cycle to analyze (ndarray as returned by the potentiostat method).
            maxima: Whether to return the maxima (True) or the minima (False) within the half cycle.

        Returns:
            peaks: List of all peaks (each one as a dictionary).
        """
        first_derivative: np.ndarray = np.gradient(half_cycle[:, 2], half_cycle[:, 1])
        second_derivative: np.ndarray = np.gradient(first_derivative, half_cycle[:, 1])
        zero_crossings: np.ndarray = np.where(np.diff(np.sign(first_derivative)))[0]

        if maxima:
            peak_indices: np.ndarray = zero_crossings[second_derivative[zero_crossings] < 0]
            peak_type: str = "Maximum"
        else:
            peak_indices: np.ndarray = zero_crossings[second_derivative[zero_crossings] > 0]
            peak_type: str = "Minimum"

        peaks = [
            {
                "peak_type": peak_type,
                "voltage": significant_digits(0.5 * (half_cycle[idx, 1] + half_cycle[idx + 1, 1]), 3),
                "current": significant_digits(0.5 * (half_cycle[idx, 2] + half_cycle[idx + 1, 2]), 3),
                "peak_idx": int(idx)
            }
            for idx in peak_indices
        ]

        return peaks

    @log_exceptions
    def _integration(
        self,
        plot: bool,
        **kwargs
    ) -> None:
        """
        Integrates the area within the CV cycle by computing the difference
        between the integral of the oxidation and the integral of the reduction cycle for every iteration.
        Saves the list of integrals to self._analysis_results.

        Args:
            plot: Whether to plot the cycle vs. integral plot.
        """
        all_relative_integrals = []
        for idx, iteration in enumerate(self._raw_data):
            integrals_per_iteration: list = []
            for cycle in iteration:
                reduction, oxidation = self._get_half_cycles(cycle)
                reduction_integral = -np.trapz(reduction[:, 2], reduction[:, 1])
                oxidation_integral = np.trapz(oxidation[:, 2], oxidation[:, 1])
                integrals_per_iteration.append(oxidation_integral - reduction_integral)
            self._analysis_results[f"Iteration {idx}"]["Integration"] = integrals_per_iteration

            relative_integrals = np.asarray(integrals_per_iteration) / max(integrals_per_iteration)
            all_relative_integrals.append(relative_integrals)

            # plot each iteration separately
            if plot:
                figure = DataVisualizer.plot_single_curve(
                    x_values=np.arange(len(iteration)) + 1,
                    y_values=relative_integrals,
                    x_label=f"CV Cycle",
                    y_label="Relative Integral",
                    title="CV Integration",
                    yaxis_percent=True
                )
                self._figures[f"CV_Integration_Iteration_{idx}"] = figure

        # plot all iterations together
        if plot:
            figure = DataVisualizer.plot_multiple_curves(
                data_to_plot=[(np.arange(len(iteration)) + 1, iteration) for iteration in all_relative_integrals],
                x_label="CV Cycle",
                y_label="Relative Integral",
                title="CV Integration",
                legend=[f"Iteration {i + 1}" for i in range(len(all_relative_integrals))]
            )
            self._figures[f"CV_Integral"] = figure

    @log_exceptions
    def _plot(
            self,
            title: str,
            **kwargs
    ) -> None:
        """
        Plots the raw data by creating a figure object, saves the figure object to self.figures.

        Args:
            title: Title of the plot
        """
        if len(self._raw_data) == 0:
            return

        for idx, iteration in enumerate(self._raw_data):
            figure = DataVisualizer.plot_multiple_curves(
                data_to_plot=[(cycle[:, 1], cycle[:, 2]) for cycle in iteration],
                x_label="Voltage / V",
                y_label="Current / A",
                title=f"{title} (Iteration {idx + 1})",
                legend=[f"Cycle {i + 1}" for i in range(len(iteration))]
            )

            self._figures[f"CV_Iteration_{idx}"] = figure

        figure = DataVisualizer.plot_multiple_curves(
            data_to_plot=[(np.vstack(iteration)[:, 1], np.vstack(iteration)[:, 2]) for iteration in self._raw_data],
            x_label="Voltage / V",
            y_label="Current / A",
            title=title,
            legend=[f"iteration {i+1}" for i in range(len(self._raw_data))]
        )
        self._figures["CV"] = figure

    @log_exceptions
    def _plot_peaks_scan_rate(self):
        """
        Generates a plot of peak voltage vs. scan rate.
        Saves the figure object to self.figures["CV_Peaks_Scanrate"].
        """
        all_peaks: list = []
        for idx, iteration in enumerate(self._raw_data):
            peaks_per_iteration: list = list(itertools.chain(*self._analysis_results[f"Iteration {idx}"]["Peak Picking"]))
            peak_positions: pd.DataFrame = pd.DataFrame(peaks_per_iteration)[["voltage", "current"]]
            peak_positions["scan_rate"] = self._get_scan_rate(iteration)
            all_peaks.append(np.array(peak_positions))

        figure = DataVisualizer.plot_multiple_points(
            data_to_plot=[(peaks[:, 2], peaks[:, 0]) for peaks in all_peaks],
            x_label="Scan Rate [V*s$^{-1}$]",
            y_label="Peak Voltage [V]",
            title="Peak Positions as a Function of Scan Rate",
            legend=[f"Iteration {i + 1}" for i in range(len(all_peaks))]
        )

        self._figures["CV_Peaks_Scanrate"] = figure

    @log_exceptions
    def _plot_currents_scan_rate(self):
        """
        Generates a plot of peak currents vs. square root of the scan rates.
        Saves the figure object to self.figures["CV_Currents_Scanrate"].
        """
        all_peaks: list = []
        for idx, iteration in enumerate(self._raw_data):
            peaks_per_iteration: list = list(itertools.chain(*self._analysis_results[f"Iteration {idx}"]["Peak Picking"]))
            peak_info: pd.DataFrame = pd.DataFrame(peaks_per_iteration)[["voltage", "current"]]
            peak_info["scan_rate_sqrt"] = self._get_scan_rate(iteration) ** 0.5
            all_peaks.append(np.array(peak_info))

        figure = DataVisualizer.plot_multiple_points(
            data_to_plot=[(peaks[:, 2], peaks[:, 1]) for peaks in all_peaks],
            x_label="Square Root of Scan Rate [V$^{0.5}$*s$^{-0.5}$]",
            y_label="Peak Current [I]",
            title="Peak Current as a Function of the Square Root of Scan Rate",
            legend=[f"Iteration {i + 1}" for i in range(len(all_peaks))]
        )

        self._figures["CV_Currents_Scanrate"] = figure
