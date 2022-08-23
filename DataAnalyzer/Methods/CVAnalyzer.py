from typing import List, Tuple
import numpy as np

from .EChemDataAnalyzer import EChemDataAnalyzer
from ..AnalysisUtils import DataVisualizer


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
        self._separate_cycles()

    def _separate_cycles(
            self
    ) -> None:
        """
        Separates the raw CV data into a list of np.ndarrays. Each ndarray represents one CV cycle.
        Overrides self._raw_data.
        """
        skip_cycles: int = 2  # TODO: figure out a more flexible way to include this
        no_cycles: int = int(np.max(self._raw_data[:, 3]))
        self._raw_data = [self._raw_data[self._raw_data[:, 3] == cycle] for cycle in range(skip_cycles, no_cycles)]

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
            **kwargs
    ) -> None:
        """
        Performs peak picking for the raw CV data.
        Divides each CV cycle into oxidation  and reduction half, and determines the maxima and minima, respectively.
        Stores all data in self._analysis_results.
        """
        all_peaks: list = []

        for cycle in self._raw_data:
            reduction, oxidation = self._get_half_cycles(cycle)
            peaks: list = self._pick_peaks(reduction, maxima=False) + self._pick_peaks(oxidation, maxima=True)
            all_peaks.append(peaks)

        self._analysis_results["Peak Picking"] = all_peaks

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
                "voltage": float(round(0.5 * (half_cycle[idx, 1] + half_cycle[idx + 1, 1]), 3)),
                "current": float(round(0.5 * (half_cycle[idx, 2] + half_cycle[idx + 1, 2]), 3)),
                "peak_idx": int(idx)
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
        between the integral of the oxidation and the integral of the reduction cycle.
        Saves the list of integrals to self._analysis_results.

        Args:
            plot: Whether to plot the cycle vs. integral plot.
        """
        integrals: list = []

        for cycle in self._raw_data:
            reduction, oxidation = self._get_half_cycles(cycle)
            reduction_integral = -np.trapz(reduction[:, 2], reduction[:, 1])
            oxidation_integral = np.trapz(oxidation[:, 2], oxidation[:, 1])
            integrals.append(float(round(oxidation_integral - reduction_integral, 3)))

        self._analysis_results["Integration"] = integrals

        relative_integrals = np.asarray(integrals) / max(integrals)

        if plot:
            figure = DataVisualizer.plot_single_curve(
                x_values=list(range(1, len(self._raw_data) + 1)),
                y_values=relative_integrals,
                x_label="CV Cycle",
                y_label="Relative Integral",
                title="CV Integration",
                yaxis_percent=True
            )

            self._figures["CV_Integration"] = figure

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
        figure = DataVisualizer.plot_multiple_curves(
            data_to_plot=[(cycle[:, 1], cycle[:, 2]) for cycle in self._raw_data],
            x_label="Voltage / V",
            y_label="Current / A",
            title=title,
            legend=[f"Cycle {i}" for i in range(1, len(self._raw_data) + 1)]
        )

        self._figures["CV"] = figure
