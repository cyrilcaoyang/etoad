from typing import List
import numpy as np
from etoad.DataAnalyzer.Methods import EChemDataAnalyzer
from etoad.DataAnalyzer.AnalysisUtils import DataVisualizer, singal_smoothing
from etoad.Utils import log_exceptions


class OCVAnalyzer(EChemDataAnalyzer):
    """
        Implementation of the EChemDataAnalyzer for open circuit voltage.

    Available analysis techniques:
        "Mean" -> Takes the mean of the voltage values
        "Plot" -> plots the voltage vs time
    """
    analysis_method_name: str = "OCV"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._raw_data = self._split_cycles(self._raw_data)
        self._smoothed_data = self._smooth(self._raw_data)

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
            "Plot": self._plot
        }

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

        # for idx, iteration in enumerate(self._raw_data):
        #     figure = DataVisualizer.plot_multiple_curves(
        #         data_to_plot=[(cycle[:, 1], cycle[:, 2]) for cycle in iteration],
        #         x_label="Time / s",
        #         y_label="Voltage / V",
        #         title=f"{title} (Iteration {idx + 1})",
        #         legend=[f"Cycle {i + 1}" for i in range(len(iteration))]
        #     )
        #
        #     self._figures[f"CV_Iteration_{idx}"] = figure

        raw_data_to_plot = [(np.vstack(iteration)[:, 1], np.vstack(iteration)[:, 2]) for iteration in self._raw_data]
        smoothed_data_to_plot = [(np.vstack(iteration)[:, 1], np.vstack(iteration)[:, 2]) for iteration in self._smoothed_data]
        legend_raw = [f"raw data iteration {i + 1}" for i in range(len(self._raw_data))]
        legend_smoothed = [f"smoothed data iteration {i + 1}" for i in range(len(self._smoothed_data))]

        figure = DataVisualizer.plot_multiple_curves(
            data_to_plot=[raw_data_to_plot + smoothed_data_to_plot],
            x_label="Time / s",
            y_label="Voltage / V",
            title=title,
            colors = ((4 / 255, 129 / 255, 69 / 255), (80 / 255, 80 / 255, 80 / 255)),
            legend=[legend_raw + legend_smoothed]
        )
        self._figures[f"OCV vs Time"] = figure
