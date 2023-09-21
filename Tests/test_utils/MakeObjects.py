import logging
from etoad.Utils import timestamp_datetime, FileHandling
from etoad.Interface import GraphicalInterface
from etoad.HardwareController.Potentiostat import EChemController
from etoad.HardwareController.SamplingSystem import SamplingSystem
from etoad.DataAnalyzer import DataAnalyzer
from etoad.WorkflowManager import WorkflowManager
from . import DataPath
from pathlib import Path
from typing import Any, Union


def mk_logger(
        task_name: str,
        sample_name: str,
        enable_gui: bool = True
) -> GraphicalInterface:
    """
    This function creates a GUI-logger for the experiment.
    """
    parent_dir, data_dir = DataPath.data_path()

    logger = GraphicalInterface(
        logging_config=parent_dir / "test_settings" / "logger_settings.yaml",
        log_file=data_dir / "Logs" / f"{timestamp_datetime()}_{sample_name}_{task_name}.log",
        enable_gui=enable_gui
    )
    logger.sample_name = sample_name
    return logger


def mk_logger_gui_free(
        task_name: str,
        sample_name: str
) -> logging.Logger:
    """
    This function creates a non-GUI-logger for the experiment.
    """
    parent_dir, data_dir = DataPath.data_path()
    logging.basicConfig(
        filename=data_dir / "Logs" / f"{timestamp_datetime()}_{sample_name}_{task_name}.log",
        format='%(asctime)s %(message)s',
        filemode='w'
    )

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def mk_sampler(
        logger: Union[GraphicalInterface, logging.Logger],
        **kwargs
) -> SamplingSystem:
    """
    This function creates a sample object with the default settings.
    """
    parent_dir, data_dir = DataPath.data_path()
    sampler = SamplingSystem(
        logger=logger,
        config_file=parent_dir / "test_settings" / "sampler_settings.yaml",
        pump_wash=0,
        cell_filled=True
    )
    return sampler


def mk_potentiostat(
        logger: Union[GraphicalInterface, logging.Logger],
        channel: int = 1,
        sim: bool = False,
        **kwargs
) -> EChemController:
    """
    This function creates a potentiostat object with the default settings.
    """
    parent_dir, data_dir = DataPath.data_path()
    potentiostat = EChemController(
        logger=logger,
        simulation_mode=sim,
        config_file=parent_dir / "test_settings" / f"potentiostat_settings_ch_{channel}.yaml",
    )
    return potentiostat


def mk_analyzer(logger: Union[GraphicalInterface, logging.Logger], **kwargs):
    """
    This function creates a data analyzer object with the default settings.
    """
    parent_dir, data_dir = DataPath.data_path()
    analyzer = DataAnalyzer(data_path=data_dir / "Data", logger=logger)
    return analyzer


def mk_workflow_manager(channel: int, enable_gui: bool, **kwargs):
    """
    This function creates a workflow manager object with the default settings.
    """
    parent_dir, data_dir = DataPath.data_path()
    workflow_manager = WorkflowManager(
        enable_gui=enable_gui,
        logfile=Path(data_dir / "Logs" / f"{timestamp_datetime()}_workflow_manager.log"),
        logger_settings=parent_dir / "test_settings" / "logger_settings.yaml",
        potentiostat_settings=parent_dir / "test_settings" / f"potentiostat_settings_ch_{channel}.yaml",
        sampler_settings=parent_dir / "test_settings" / "sampler_settings.yaml",
        data_path=data_dir / "DATA",
    )
    return workflow_manager


def mk_csv(
        results: Any,
        logger: Union[GraphicalInterface, logging.Logger],
        **kwargs
):
    """
    This script saves raw data into CSV files.
    """
    parent_dir, data_dir = DataPath.data_path()
    filename = data_dir / "Data" / f"{logger.experiment_name}_{logger.sample_name}_{timestamp_datetime()}.csv"
    FileHandling.save_as_csv(results, filename)
    logger.info(f"{logger.experiment_name} of {logger.sample_name} is saved as {filename}.")
