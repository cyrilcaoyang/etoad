from typing import List
import numpy as np
from etoad.DataAnalyzer.Methods import EChemDataAnalyzer
from etoad.DataAnalyzer.AnalysisUtils import DataVisualizer, signal_smoothing, noise_estimation
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
        self._smoothed_data = signal_smoothing.smooth(2, self._raw_data, polyorder=2)

    def _set_methods(self):
        """
        Implementation of the abstract method.
        Sets the self._analysis_methods attribute as the factory pattern
        """
        self._analysis_methods = {
            "Fin Voltage": self._fin_voltage,
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

        raw_data_to_plot = [(np.vstack(iteration)[:, 1], np.vstack(iteration)[:, 2]) for iteration in self._raw_data]
        smoothed_data_to_plot = [(np.vstack(iteration)[:, 1], np.vstack(iteration)[:, 2]) for iteration in self._smoothed_data]
        legend_raw = [f"raw data iteration {i + 1}" for i in range(len(self._raw_data))]
        legend_smoothed = [f"smoothed data iteration {i + 1}" for i in range(len(self._smoothed_data))]

        figure = DataVisualizer.plot_multiple_curves(
            data_to_plot=raw_data_to_plot+ smoothed_data_to_plot,
            x_label="Time / s",
            y_label="Voltage / V",
            title=title,
            colors=(
                (10 / 255, 255 / 255, 10 / 255),
                (255 / 255, 10 / 255, 10 / 255),
                (10 / 255, 10 / 255, 255 / 255),
                (80 / 255, 200 / 255, 200 / 255),
            ),
            legend=legend_raw + legend_smoothed,
        )
        self._figures[f"OCV vs Time"] = figure

    @log_exceptions
    def _fin_voltage(self) -> (float, bool):
        """
        Calculate the final voltage of the experiment
        Returns:
            bool: True if the voltage is stable in the last 10 seconds of the experiment
        """
        for i, iteration in enumerate(self._raw_data):
            column = np.vstack(iteration)[:, 2]
            final_voltage, stability = self._is_voltage_stable(column)
            self._analysis_results[f"Iteration {i}"]["Is Voltage Stable"] = stability
            self._analysis_results[f"Iteration {i}"]["Final Voltage"] = final_voltage

    @staticmethod
    def _is_voltage_stable(column: np.ndarray) -> (float, bool):
        """
        Calculate the final voltage of the experiment
        Returns:
            float: average of the last quarter/20 points of the voltage values
            bool: true if the voltage is stable in the last quarter/20 points of the experiment/iteration
        """
        quarter = min(20, len(column) // 4)
        avg_first = np.mean(column[0:quarter])
        avg_mid = np.mean(column[len(column) // 2 - quarter // 2:len(column) // 2 + quarter // 2])
        avg_last = np.mean(column[-quarter:])
        avg_last_d5 = "{:.5f}".format(avg_last)
        if abs(avg_first - avg_last) > np.std(column[-quarter:]):
            return avg_last_d5, False
        elif abs(avg_mid - avg_last) > np.std(column[-quarter:]):
            return avg_last_d5, False
        else:
            return avg_last_d5, True
