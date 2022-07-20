import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Union, Any, Optional
import numpy as np

from Utils import get_logger
from Utils import save_as_pkl, save_as_csv
from Utils import timestamp_datetime
from Utils import ConfigLoader
from Utils import SkipExecution, StopExecution
from HardwareController import EChemController, SamplingSystem


class WorkflowManager(object):
    """
    High-level controller to perform complex pre-defined workflows for electrochemical compound characterization.
    Manages the following processes:
        - sample preparation and sample transfer (via the SamplingSystem package)
        - electrochemical measurements (via the EChemController package)
        - data analysis (via the EChemAnalyzer package) and downstream decision-making
        - data storage

    For a detailed description of the workflow settings file (json format), see documentation.

    Public methods:
        measure_sample(sample_name: str, sample_location: int, workflow_path: Path) -> None
    """
    # TODO: include threading

    _required_settings: set = {
        "Protocol Name",
        "Steps",
        "Sample Volume",
        "Total Volume",
        "Purge",
        "Wash"
    }

    _exception_keywords: dict = {
        "SKIP": SkipExecution,
        "STOP": StopExecution
    }

    def __init__(
            self,
            logger_settings: Path,
            potentiostat_settings: Path,
            sampler_settings: Path,
            data_path: Path,
            logfile: Optional[Path] = None
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
            logfile: Optional - name of the logfile used.
        """
        self.logger: logging.Logger = get_logger(logger_settings, logger_name="EChem", logfile=logfile)  # TODO: Make more flexible?
        self.logger.info("SYSTEM INITIALIZATION")

        self.potentiostat: EChemController = EChemController(potentiostat_settings, logger=self.logger)
        self.sampling_system: SamplingSystem = SamplingSystem(sampler_settings, logger=self.logger)
        self.analyzer: None = None  # TODO: implement Jackie's data analyzer
        self.data_path: Path = data_path

    def measure_sample(
            self,
            sample_name: str,
            sample_location: int,
            workflow_path: Path
    ) -> dict:
        """
        Executes a specified measurement workflow for a given sample.

        Args:
            sample_name: Name of the sample to be measured
            sample_location: Position of the sample on the autosampler.
            workflow_path: Path to the json file that specifies the workflow to be executed.

        Returns:
            result: Dictionary of all steps executed and their respective results.
        """
        workflow: dict = ConfigLoader.load_config(workflow_path, self._required_settings)
        self.logger.info(f"Starting Protocol {workflow['Protocol Name']} for sample {sample_name}.")

        result: dict = {"Sample Name": sample_name, "Workflow": workflow["Protocol Name"]}

        with self._sample_in_cell(sample_location, workflow["Sample Volume"], workflow["Total Volume"], workflow["Purge"], **workflow["Wash"]):
            for step, step_details in zip(workflow["Steps"], workflow["Steps"].values()):
                try:
                    result: dict = self._execute_step(sample_name, step, result, **step_details)
                except SkipExecution:
                    continue
                except StopExecution:
                    break

        return result

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
            step_name: Name of the step to be executed (key in the settings file).
            previous_results: Dictionary of all results from previous steps.
            kwargs: Keyword arguments for the specific step to be executed.
        """
        executable_steps: dict = {
            "measure": self._run_measurement,
            "dilute": self._dilute_cell,
        }
        self.logger.info(f"Now executing {step_name}.")
        # TODO: implement data saving as individual step with details?

        return executable_steps[kwargs["task"]](sample_name, step_name, previous_results, **kwargs)

    @contextmanager
    def _sample_in_cell(
            self,
            autosampler_position: int,
            sample_volume: float,
            total_volume: float,
            purge_time: float,
            wash_volume: float = 5,
            washing_cycles: int = 3
    ) -> None:
        """
        Context manager for transferring a sample to the measurement cell (before the first measurement),
        and emptying and washing the cell (after the final measurement).

        Args:
             autosampler_position: Vial number on the autosampler.
             sample_volume: Volume to be transferred to the cell.
             total_volume: Total volume of the sample in the cell (after dilution).
             purge_time: Time for purging with nitrogen gas.
             wash_volume: Volume to wash the cell.
             washing_cycles: Iterations for washing the cell
        """
        self.sampling_system.transfer_to_cell(autosampler_position, sample_volume, wash_line=True)
        self.sampling_system.dilute_cell(volume=total_volume-sample_volume)
        self.logger.info(f"Sample was successfully transferred to the measurement cell ({sample_volume}+{total_volume-sample_volume} mL).")
        self.sampling_system.purge_cell(purge_time)
        try:
            yield
        finally:
            self.logger.info(f"Measurements for sample completed.")
            self.sampling_system.wash_cell(wash_volume, washing_cycles)

    def _run_measurement(
            self,
            sample_name: str,
            step_name: str,
            results: dict,
            technique: str,
            parameters: dict,
            update_parameters: list,
            channel: Union[int, None] = None,
            **kwargs
    ) -> dict:
        """
        Runs a specified measurement on the instrument by loading the technique, running the measurement and evaluating
        the data.

        Args:
            sample_name: Name of the measurement.
            step_name: Name of the step to be executed.
            results: Dictionary for storing all previous results.
            technique: Name of the measurement technique
            parameters: Dictionary of measurement parameters deviating from the default values.
            update_parameters: List of dictionaries of parameters that need to be inferred from previous measurements.
            channel: Measurement channel (if None, the default channel is selected).
        """
        if update_parameters:
            parameters = self._update_parameters(update_parameters, parameters, results)

        self.potentiostat.load_technique(technique, parameters, channel)
        raw_data: np.ndarray = self.potentiostat.do_measurement(channel)

        analysis_results: dict = {}  # self.analyzer.analyze_data(technique, parameters, raw_data)  # TODO: double-check once analyzer is implemented
        self._save_data(sample_name, step_name, raw_data, analysis_results)
        results[step_name] = analysis_results
        return results

    def _save_data(
            self,
            sample_name: str,
            step_name: str,
            raw_data: np.ndarray,
            analysis_results: dict
    ) -> None:
        """
        Saves the experimental results (raw data as .pkl and analysis results as .csv) into a folder
        named after the sample name. Creates this folder if it does not exist.

        Args:
             sample_name: Name of the sample
             step_name: Name of the executed step
             raw_data: Raw experimental results, as returned by the potentiostat.
             analysis_results: Results of the experimental analysis
        """
        sample_dir = self.data_path / sample_name
        sample_dir.mkdir(parents=True, exist_ok=True)

        file_basename = f"{sample_name}_{step_name}_{timestamp_datetime()}"

        save_as_pkl(raw_data, sample_dir / f"{file_basename}.pkl")
        save_as_csv(analysis_results, sample_dir / f"{file_basename}.csv")

    def _dilute_cell(
            self,
            sample_name: str,
            step_name: str,
            results: dict,
            **kwargs
    ):
        """
        Executes the dilution of the sample in the measurement cell by calling the method from the
        sampling system object.

        Args:
            sample_name: Name of the sample                   ATTN: Only required for uniform code structure.
            step_name: Name of the step                       ATTN: Only required for uniform code structure.
            results: Dictionary of previous results
            kwargs: Keyword arguments for the dilute_cell method (either "volume" or "factor")
        """
        self.sampling_system.dilute_cell(**kwargs)
        results["dilution"] = True

        return results

    def _update_parameters(
            self,
            update_settings: list,
            parameters: dict,
            previous_results: dict
    ) -> dict:
        """
        Updates the parameter dictionary from the results of previous measurements.

        Structure of the update_settings list:
        [
            {
                "parameter": Name of the parameter to be updated
                "from measurement": Name of the measurement performed
                "key": Key in the results dictionary for this measurement.
            },
            ...
        ]

        Args:
            update_settings: List of parameters to be updated (structure see above).
            parameters: Dictionary of measurement parameters to be passed to the potentiostat.
            previous_results: Dictionary of all previous results.

        Raises:
            WorkflowException (according to keywords in self._exception_keywords) if skipping / cancelling is triggered.
        """
        for param_to_update in update_settings:
            new_value: Any = previous_results[param_to_update["from measurement"]][param_to_update["key"]]

            if new_value in self._exception_keywords:
                raise self._exception_keywords[new_value]

            parameters[param_to_update["parameter"]] = new_value

        return parameters
