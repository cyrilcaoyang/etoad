from typing import List, Tuple
import numpy as np
import pandas as pd
from .EChemDataAnalyzer import EChemDataAnalyzer
from ..AnalysisUtils import DataVisualizer
import itertools


class CVAnalyzer(EChemDataAnalyzer):
    """
    Implementation of the EChemDataAnalyzer for cyclic voltammetry.

    Available analysis techniques:
        "Peak Picking" -> selects and characterizes peaks
        "Integration" -> determines the integral within each CV cycle
        "Plot" -> plots the voltammograms
    """
    analysis_method_name: str = "CV"

    def __init__(self, *args):
        super().__init__(*args)
        self._separate_iterations()
        self._separate_cycles()

    def _separate_cycles(
            self
    ) -> None:
        """
        Separates the dictionary of np.ndarrys into a dictionary of lists of np.ndarrays.
        Each ndarray represents one CV cycle.
        Overrides self._raw_data.
        """
        for iteration, iteration_data in zip(self._raw_data.keys(), self._raw_data.values()):
            skip_cycles: int = 2  # TODO: figure out a more flexible way to include this
            no_cycles: int = int(np.max(iteration_data[:, 3]) + 1)
            self._raw_data[iteration] = [iteration_data[iteration_data[:, 3] == cycle] for cycle in range(skip_cycles, no_cycles)]

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
            "Peaks scanrate": self._plot_peaks_scanrate,
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

    def _peak_picking(
            self,
            plot: bool,
            **kwargs
    ) -> None:
        """
        Performs peak picking for the raw CV data.
        Divides each CV cycle into oxidation and reduction half, and determines the maxima and minima, respectively.
        Stores all data in self._analysis_results.

        Args:
            plot: Whether to plot the diagram peak position vs iteration
        """
        for iteration in self._raw_data.keys():
            peaks_per_iteration: list = []
            for cycle in self._raw_data[iteration]:
                reduction, oxidation = self._get_half_cycles(cycle)
                peaks: list = self._pick_peaks(reduction, maxima=False) + self._pick_peaks(oxidation, maxima=True)
                peaks_per_iteration.append(peaks)
            self._analysis_results[iteration]["Peak Picking"] = peaks_per_iteration

    @staticmethod
    def _get_scan_rate(data_of_one_cycle: np.ndarray) -> float:
        """
        Acquire the scan rate of this cycle in the unit of V/s.

        Args:
            data_of_one_cycle: Data of a full cycle in CV data

        Returns:
            scan_rate: The scan rate of this cycle in V/s
        """
        time_series = data_of_one_cycle[:,0]
        voltage_series = data_of_one_cycle[:,1]
        scan_rate = (np.max(voltage_series)-np.min(voltage_series))*2/(np.max(time_series)-np.min(time_series))
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
                "voltage": 0.5 * (half_cycle[idx, 1] + half_cycle[idx + 1, 1]),
                "current": 0.5 * (half_cycle[idx, 2] + half_cycle[idx + 1, 2]),
                "peak_idx": idx
            }
            for idx in peak_indices
        ]

        return peaks

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
        for iteration in self._raw_data.keys():
            integrals_per_iteration: list = []
            for cycle in self._raw_data[iteration]:
                reduction, oxidation = self._get_half_cycles(cycle)
                reduction_integral = -np.trapz(reduction[:, 2], reduction[:, 1])
                oxidation_integral = np.trapz(oxidation[:, 2], oxidation[:, 1])
                integrals_per_iteration.append(oxidation_integral - reduction_integral)
            self._analysis_results[iteration]["Integration"] = integrals_per_iteration

            relative_integrals = np.asarray(integrals_per_iteration) / max(integrals_per_iteration)

            if plot:
                figure = DataVisualizer.plot_single_curve(
                    x_values=list(range(1, len(self._raw_data[iteration]) + 1)),
                    y_values=relative_integrals,
                    x_label=f"CV Cycle_{iteration}",
                    y_label="Relative Integral",
                    title="CV Integration",
                    yaxis_percent=True
                )

                self._figures[f"CV_Integration_{iteration}"] = figure

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
        # ATTN: Do we always want to generate one plot per iteration, or do we want the option to get all data
        #       in one plot? (FSK, Sep 13)

        for iteration in self._raw_data.keys():
            figure = DataVisualizer.plot_multiple_curves(
                data_to_plot=[(cycle[:, 1], cycle[:, 2]) for cycle in self._raw_data[iteration]],
                x_label="Voltage / V",
                y_label="Current / A",
                title=title+f"_{iteration}",
                legend=[f"Cycle {i}" for i in range(1, len(self._raw_data[iteration]) + 1)]
            )

            self._figures[f"CV_{iteration}"] = figure

    def _plot_peaks_scanrate(self):
        """
        Plot Peaks_Voltage vs Scanrate and save the figure object in self.figures["CV_Peaks_Scanrate"]
        """

        all_peaks: list = []
        for iteration in self._analysis_results.keys():
            peaks_per_iteration: list = list(itertools.chain(*self._analysis_results[iteration]["Peak Picking"]))
            peaks_position: pd.DataFrame = pd.DataFrame(peaks_per_iteration)[
                ["voltage", "current"]]  # TODO: Why are you using a pandas dataframe here?
            peaks_position["scan_rate"] = self._get_scan_rate(self._raw_data[iteration][0])
            # ATTN: How much sense does it make to infer the scan rate from the raw data?
            #       -> The scan rate is already pre-defined by the measurement parameters, and should be taken
            #          from there
            #          (not an urgent fix, but something to keep in mind, FSK, Sep 13)
            all_peaks.append(np.array(peaks_position))

        figure = DataVisualizer.plot_multiple_curves(
            data_to_plot=[(peaks_per_iteration[:, 2], peaks_per_iteration[:, 0]) for peaks_per_iteration in all_peaks],
            x_label="Scan Rate / V*sec^-1",
            y_label="Voltage / V",
            title="Peaks vs Scanrate",
            legend=[f"Iteration {i}" for i in range(1, len(all_peaks) + 1)]
        )

        self._figures["CV_Peaks_Scanrate"] = figure
