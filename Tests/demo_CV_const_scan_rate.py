import threading
import numpy
from pathlib import Path

from etoad.HardwareController.Potentiostat.EChemController import EChemController
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime, ThreadWithReturn

"""
    This python script demonstrate the CV scans with constant scan rates.
"""

# ========== Sample Settings Below ========== #

Sample_Name = "K4[Fe(CN)6]"
V_init = 0                  # Unit: Initial Voltage in V
V_max = 0.5                 # Unit: Highest Voltage in V
V_min = 0                   # Unit: Lowest Voltage in V
V_fin = 0                   # Unit: Final Voltage in V
Scan_Rate = 0.050           # Unit: Scan Rate in V/s
Cycle_Numbers: int = 10     # The Numer of Cycles as an Integer

Disable_GUI: bool = False
Simulation: bool = False    # This option can turn ON/OFF the Simulation Mode

# ========== Sample Settings Above ========== #


def define_paths() -> tuple:
    """
    This function defines the path of the working and data directory.
    """
    parent_dir = Path(__file__).parent
    with open(parent_dir / "test_settings" / "file_settings") as file:
        data_dir = Path(file.read())
    return parent_dir, data_dir


def make_logger(disable_gui: bool) -> GraphicalInterface:
    """
    This function creates a logger for the experiment.
    """
    parent_dir, data_dir = define_paths()
    logger = GraphicalInterface(
        logging_config=parent_dir / "test_settings" / "logger_settings.json",
        log_file=data_dir / "Logs" / f"{timestamp_datetime()}_{Sample_Name}_CV_const_scan_rate.log",
        disable_gui=disable_gui
    )
    return logger


def do_measurement(sample_name: str, simulation_mode: bool, logger: GraphicalInterface) -> None:

    parent_dir, data_dir = define_paths()
    potentiostat = EChemController(
        config_file=parent_dir / "test_settings" / "potentiostat_settings.json",
        logger=logger,
        simulation_mode=simulation_mode,
    )

    logger.sample_name = sample_name
    logger.info(f"Starting Experiment: CV Scans of {logger.sample_name}.")

    results = potentiostat.do_measurement(
        technique="CV",
        set_parameters={
            "IterationSettings": {
                "no_iterations": 1
            },
            "TechniqueParameters": {
                "Voltage Profile": {
                    "value": [V_init, V_max, V_min, V_init, V_fin]
                },
                "Scan Rate": {
                    "value": [Scan_Rate, Scan_Rate, Scan_Rate, Scan_Rate, Scan_Rate]
                },
                "Number of Cycles": {
                    "value": Cycle_Numbers
                }
            }
        }
    )

    # saving the data before disconnection
    filename = data_dir / "Data" / f"CV_Const_ScanRate_{logger.sample_name}_{timestamp_datetime()}.csv"
    numpy.savetxt(filename, results, delimiter=',')
    logger.info(f"Result of CV scans of {logger.sample_name} is saved as {filename}.")
    potentiostat.disconnect()
    logger.stop_gui()


if __name__ == "__main__":

    logger = make_logger(Disable_GUI)
    worker_thread = ThreadWithReturn(target=do_measurement, args=(Sample_Name, Simulation, logger))
    worker_thread.start()
    logger.start_gui()
    worker_thread.join()


