from typing import List
import numpy as np
from .EChemDataAnalyzer import EChemDataAnalyzer
from ..AnalysisUtils import DataVisualizer, noise_estimation
from ...Utils import log_exceptions


class OCVAnalyzer(EChemDataAnalyzer):
    """
    """
    analysis_method_name: str = "OCV"

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

        data_separated: List[List[np.ndarray]] = []
        for idx, iteration in enumerate(data):
            no_cycles: int = int(np.max(iteration[:, 3]) + 1)
            data_separated.append([iteration[iteration[:, 3] == cycle] for cycle in range(no_cycles)])

        return data_separated

    def _set_methods(self):
        """
        Implementation of the abstract method.
        Sets the self._analysis_methods attribute as the factory pattern
        """
        self._analysis_methods = {
            "Average": self._mean,
            "Plot": self._plot
        }

    @log_exceptions
    def _mean(self):
        """
        Calculates the mean of the raw data and saves the result to self._results.
        """
        if len(self._raw_data) == 0:
            return
        self._analysis_results["Average"] = np.mean(np.vstack(self._raw_data)[:, 2])

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
                x_label="Time / s",
                y_label="Voltage / V",
                title=f"{title} (Iteration {idx + 1})",
                legend=[f"Cycle {i + 1}" for i in range(len(iteration))]
            )

            self._figures[f"CV_Iteration_{idx}"] = figure

        figure = DataVisualizer.plot_multiple_curves(
            data_to_plot=[(np.vstack(iteration)[:, 1], np.vstack(iteration)[:, 2]) for iteration in self._raw_data],
            x_label="Time / s",
            y_label="Voltage / V",
            title=title,
            legend=[f"iteration {i + 1}" for i in range(len(self._raw_data))]
        )
        self._figures["OCV"] = figure

