import numpy
from pathlib import Path

from etoad.HardwareController.Potentiostat.EChemController import EChemController
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime, ThreadWithReturn
from etoad.DataAnalyzer import DataAnalyzer

"""
    This python script demonstrate the CV scans with multiple different scan rates.
    Without the usage of the GUI, the experiment can be run in the background.
"""

# ========== Sample Settings Below ========== #

Sample_Name = "K4[Fe(CN)6]"
V_init = 0                  # Unit: Initial Voltage in V
V_max = 0.5                 # Unit: Highest Voltage in V
V_min = 0                   # Unit: Lowest Voltage in V
V_fin = 0                   # Unit: Final Voltage in V

Scan_Rates = [0.400, 1.000]    # Unit: Scan Rate in V/s [0.050, 0.100, 0.200, 0.400, 1.000]
Cycle_Numbers: int = 3      # The Numer of Cycles at each Scan Rate

Disable_GUI: bool = False
Simulation: bool = False    # This option can turn ON/OFF the Simulation Mode

# ========== Sample Settings Above ========== #

"""
Demonstration of Iterations of CV scans with various scan rates. 
"""


def define_paths() -> tuple:
    """
    This function defines the path of the working and data directory.
    """
    parent_dir = Path(__file__).parent
    with open(parent_dir / "test_settings" / "file_settings") as file:
        data_dir = Path(file.read())
    return parent_dir, data_dir


def make_logger(sample_name: str, disable_gui: bool) -> GraphicalInterface:
    """
    This function creates a logger for the experiment.
    """
    parent_dir, data_dir = define_paths()
    logger = GraphicalInterface(
        logging_config=parent_dir / "test_settings" / "logger_settings.json",
        log_file=data_dir / "Logs" / f"{timestamp_datetime()}_{sample_name}_CV_multi_scan_rate.log",
        disable_gui=disable_gui
    )
    logger.sample_name = sample_name
    return logger


def do_measurement(scan_rates: list, simulation_mode: bool, logger: GraphicalInterface):

    num_iter = len(scan_rates)
    list_scan_rates = [[scan_rates[i] for _ in range(5)] for i in range(num_iter)]

    parent_dir, data_dir = define_paths()
    potentiostat = EChemController(
        config_file=parent_dir / "test_settings" / "potentiostat_settings.json",
        logger=logger,
        simulation_mode=False,
    )
    logger.info(f"Starting Experiment: CV scans of {logger.sample_name} at Various Scan Rates.")
    logger.info(f"Starting measurements of {num_iter} iterations:")

    results = potentiostat.do_measurement(
        technique="CV",
        set_parameters={
            "IterationSettings": {
                "no_iterations": num_iter
            },
            "TechniqueParameters": {
                "Voltage Profile": {
                    "value": [V_init, V_max, V_min, V_init, V_fin]
                },
                "Scan Rate": {
                    "changed_over_iterations": True,
                    "value": list_scan_rates
                },
                "Number of Cycles": {
                    "value": Cycle_Numbers
                }
            }
        }
    )

    # saving the data before disconnection
    filename = data_dir / "Data" / f"CV_Multi_ScanRate_{logger.sample_name}_{timestamp_datetime()}.csv"
    numpy.savetxt(filename, results, delimiter=',')
    logger.info(f"Result of CV scans of {logger.sample_name} is saved as {filename}.")
    potentiostat.disconnect()

    analyzer = DataAnalyzer(
        data_path=data_dir / "Data", logger=logger
    )
    analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="CV",
        analysis_settings={
            "Plot": {
                "title": "Cyclic Voltammetry of Multiple Scans"
            },
            "Peak Picking": {},
            "Integration": {}
        },
        raw_data=results
    )

    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = make_logger(Sample_Name, Disable_GUI)
    worker_thread = ThreadWithReturn(target=do_measurement, args=(Scan_Rates, Simulation, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()

# TODO: Add Analysis of results, and Plots
