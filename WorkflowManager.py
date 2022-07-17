import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Union, Any
import numpy as np

from Utils import get_logger, save_as_pkl, save_as_csv, timestamp_datetime, ConfigLoader
from HardwareController import EChemController, SamplingSystem


class WorkflowManager(object):
    """
    Documentation for a Workflow Manager.
    """

    required_settings: set = {}  # TODO: include the keys required for a valid workflow

    def __init__(
            self,
            logger_settings: Path,
            potentiostat_settings: Path,
            sampler_settings: Path,
            data_path: Path
    ):
        """
        Instantiates the workflow manager object by instantiating the individual modules:
            - self.logger
            - self.potentiostat (EChemController object)
            - self.sampling_system (SamplingSystem object)
            - self.analyzer (DataAnalyzer object)

        Args:
            logger_settings: Path to the json file containing the logger settings
            potentiostat_settings: Path to the json file containing the potentiostat settings
            sampler_settings: Path to the json file containing the sampler settings
            data_path: Path to the folder where data should be stored.
        """
        self.logger: logging.Logger = get_logger(logger_settings, logger_name="EChem")  # TODO: Make more flexible?
        self.potentiostat: EChemController = EChemController(potentiostat_settings, logger=self.logger)
        self.sampling_system: SamplingSystem = SamplingSystem(sampler_settings, logger=self.logger)
        self.analyzer: None = None  # TODO: implement Jackie's data analyzer
        self.data_path: Path = data_path

    def measure_sample(
            self,
            sample_name: str,
            sample_location: int,
            workflow_path: Path
    ) -> None:
        """
        Executes a specified measurement workflow for a given sample.

        Args:
            sample_name: Name of the sample to be measured
            sample_location: Position of the sample on the autosampler.
            workflow_path: Path to the json file that specifies the workflow to be executed.
        """
        workflow: dict = ConfigLoader.load_config(workflow_path)

        with self._sample_in_cell(sample_location, workflow["sample_volume"], **workflow["wash"]):
            for step in workflow["steps"]:  # TODO: double-check the architecture of the workflow file
                try:
                    result: dict = self._execute_step(step, sample_name, result, **workflow["steps"][step])
                except StopIteration:
                    break  # TODO: include more advanced exception handling here, especially for decision making methods

    def _execute_step(
            self,
            sample_name: str,
            step_name: str,
            previous_results: dict,
            **kwargs
    ) -> Any:
        """
        Factory pattern for executing a specific operation, as specified in the workflow.

        Args:
            sample_name: Name of the sample to be run.
            step_name: Name of the operation to be executed.
            previous_results: Dictionary of all results from previous steps.
            kwargs: Keyword arguments for the specific step to be executed.
        """
        executable_steps: dict = {
            "measure": self._run_measurement,
            "dilute": self._dilute_cell,
        }

        # TODO: infer parameters and settings from previous steps etc
        # TODO: additional methods for decision making?
        # TODO: exception handling

        return executable_steps[step_name](sample_name, previous_results, **kwargs)

    @contextmanager
    def _sample_in_cell(
            self,
            autosampler_position: int,
            sample_volume: float,
            wash_volume: float,
            washing_cycles: int = 3
    ) -> None:
        """
        Context manager for transferring a sample to the measurement cell (before the first measurement),
        and emptying and washing the cell (after the final measurement).

        Args:
             autosampler_position: Vial number on the autosampler.
             sample_volume: Volume to be transferred to the cell.
             wash_volume: Volume to wash the cell.
             washing_cycles: Iterations for washing the cell
        """
        self.sampling_system.transfer_to_cell(autosampler_position, sample_volume)
        try:
            yield
        finally:
            self.sampling_system.wash_cell(wash_volume, washing_cycles)

    def _run_measurement(
            self,
            sample_name: str,
            results: dict,
            technique: str,
            parameters: dict,
            channel: Union[int, None] = None
    ) -> dict:
        """
        Runs a specified measurement on the instrument by loading the technique, running the measurement and evaluating
        the data.

        Args:
            sample_name: Name of the measurement
            results: Dictionary for storing all previous results.
            technique: Name of the measurement technique
            parameters: Dictionary of measurement parameters deviating from the default values.
            channel: Measurement channel (if None, the default channel is selected).
        """
        # TODO: include threading
        self.potentiostat.load_technique(technique, parameters, channel)
        raw_data: np.ndarray = self.potentiostat.do_measurement(channel)

        analysis_results: dict = self.analyzer.analyze_data(technique, parameters, results)  # TODO: double-check once analyzer is implemented
        self._save_data(sample_name, technique, raw_data, analysis_results)
        results[technique] = analysis_results

        return results

    def _save_data(
            self,
            sample_name: str,
            technique: str,
            raw_data: np.ndarray,
            analysis_results: dict
    ) -> None:
        """
        Saves the experimental results (raw data as .pkl and analysis results as .csv) into a folder
        named after the sample name. Creates this folder if it does not exist.

        Args:
             sample_name: Name of the sample
             technique: Name of the measurement technique
             raw_data: Raw experimental results, as returned by the potentiostat.
             analysis_results: Results of the experimental analysis  # TODO: maybe change that to a dictionary?
        """
        sample_dir = self.data_path / sample_name
        sample_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{sample_name}_{technique}_{timestamp_datetime()}"

        save_as_pkl(raw_data, sample_dir / f"{file_name}.pkl")
        save_as_csv(analysis_results, sample_dir / f"{file_name}.csv")

    def _dilute_cell(
            self,
            sample_name: str,
            results: dict,
            **kwargs
    ):
        """
        Executes the dilution of the sample in the measurement cell by calling the method from the
        sampling system object.

        Args:
            sample_name: Name of the sample  ATTN: Only required for uniform code structure.
            results: Dictionary of previous results
            kwargs: Keyword arguments for the dilute_cell method (either "volume" or "factor")
        """
        self.sampling_system.dilute_cell(**kwargs)
        results["dilution"] = True

        return results
