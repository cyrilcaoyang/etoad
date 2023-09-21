import numpy as np
from etoad.DataAnalyzer.Methods import EChemDataAnalyzer
from etoad.DataAnalyzer.AnalysisUtils import DataVisualizer, signal_smoothing
from etoad.Utils import log_exceptions


class OCVAnalyzer(EChemDataAnalyzer):
    """
        Implementation of the EChemDataAnalyzer for open circuit voltage.

    Available analysis techniques:
        "Voltage" -> Takes the mean of the voltage values
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
            "Voltage": self._fin_voltage,
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
                (80 / 255, 80 / 255, 80 / 255),
                (10 / 255, 10 / 255, 10 / 255),
            ),
            legend=legend_raw + legend_smoothed,
        )
        self._figures[f"OCV vs Time"] = figure

    @log_exceptions
    def _fin_voltage(self) -> (float, bool):
        """
        Calculate the final voltage of the experiment
        Returns:
            float: final voltage of the experiment
            bool: True if the voltage is stable in the last 10 seconds of the experiment
        """
        for i, iteration in enumerate(self._raw_data):
            column = np.vstack(iteration)[:, 2]
            stability = self.is_step_stable(column, 1.10)
            v_average = "{:.5f}".format(np.mean(iteration[:, 2]))
            v_std_dev = "{:.5f}".format(np.std(iteration[:, 2]))
            self._analysis_results[f"Iteration {i}"]["Is Voltage Stable"] = stability
            self._analysis_results[f"Iteration {i}"]["Voltage Average"] = v_average
            self._analysis_results[f"Iteration {i}"]["Voltage Std Deviation"] = v_std_dev
            self._analysis_results[f"Iteration {i}"]["CV Parameters"] = [v_average, None, None, v_average, None]
            # The default parameters will not be over-written by the None values.

    @staticmethod
    @log_exceptions
    def is_step_stable(column: np.ndarray, threshold: float) -> bool:
        """
        Calculate the mean voltage and standard deviation of the last quarter/20 points of the experiment/iteration
        The voltage is not stable, if:
            1. the difference b/w the mean of the 1st and last quarter > the standard deviation of the last quarter,
            2. the standard deviation of the mid-quarter > threshold * the standard deviation of the last quarter

        Returns:
            float: average of the last quarter/20 points of the voltage values
            bool: true if the voltage is stable in the last quarter/20 points of the experiment/iteration
        """
        if threshold <= 1:
            raise ValueError("Threshold must be greater than 1")

        quarter = max(20, len(column)//4)
        avg_first_q = float("{:.5f}".format(np.mean(column[:quarter])))
        avg_last_q = float("{:.5f}".format(np.mean(column[-quarter:])))
        if abs(avg_first_q - avg_last_q) > np.std(column[-quarter:]):
            return False
        elif np.std(column[len(column)//2 - quarter//2:len(column)//2 + quarter//2]) >\
                threshold * np.std(column[-quarter:]):
            return False
        else:
            return True
