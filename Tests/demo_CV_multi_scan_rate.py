import numpy
from pathlib import Path

from etoad.HardwareController.Potentiostat.EChemController import EChemController
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime
from etoad.Utils import ThreadWithReturn
from etoad.DataAnalyzer import DataAnalyzer

"""
    This python script demonstrate the CV scans with multiple different scan rates.
    Without the use of WorkflowManager.
    The user can define the parameters of the CV scans below.
"""

# ========== Sample Settings Below ========== #

Sample_Name = "K4[Fe(CN)6]"
V_init = 0                  # Unit: Initial Voltage in V
V_max = 0.5                 # Unit: Highest Voltage in V
V_min = 0                   # Unit: Lowest Voltage in V
V_fin = 0                   # Unit: Final Voltage in V
Cycle_Numbers: int = 3      # The Numer of Cycles at each Scan Rate

Scan_Rates = {0.500, 1.000}    # Unit: Scan Rate in V/s
# Scan_Rates = {0.050, 0.100, 0.200, 0.400, 1.000}    # Unit: Scan Rate in V/s

Disable_GUI: bool = False
Simulation: bool = False    # This option can turn ON/OFF the Simulation Mode

# ========== Sample Settings Above ========== #


def go_measurement(
        v_init=V_init, v_max=V_max, v_min=V_min, v_fin=V_fin,
        cycle_numbers=Cycle_Numbers,
        scan_rates=tuple(Scan_Rates),
        simulation=Simulation,
        _data_dir: Path = None,
        _parent_dir: Path = None,
        _logger: GraphicalInterface = None,
):

    # Calculates the number of iterations, and creates a list of scan rates for each iteration
    num_iter = len(scan_rates)
    list_scan_rates = [[scan_rates[i] for _ in range(5)] for i in range(num_iter)]

    # Instantiates the potentiostat and reads the settings from the potentiostat_settings.json file
    potentiostat = EChemController(
        config_file=_parent_dir / "test_settings" / "potentiostat_settings.json",
        logger=_logger,
        simulation_mode=simulation,
    )

    # Connects to the potentiostat and performs the CV scans.
    results = potentiostat.do_measurement(
        technique="CV",
        set_parameters={
            "IterationSettings": {
                "no_iterations": num_iter
            },
            "TechniqueParameters": {
                "Voltage Profile": {
                    "value": [v_init, v_max, v_min, v_init, v_fin]
                },
                "Scan Rate": {
                    "changed_over_iterations": True,
                    "value": list_scan_rates
                },
                "Number of Cycles": {
                    "value": cycle_numbers
                }
            }
        }
    )

    # Saves the data before disconnecting from the potentiostat.
    filename = _data_dir / "Data" / f"CV_Multi_ScanRate_{_logger.sample_name}_{timestamp_datetime()}.csv"
    numpy.savetxt(filename, results, delimiter=',')
    _logger.info(f"Result of CV scans of {_logger.sample_name} is saved as {filename}.")
    potentiostat.disconnect()

    # Analyzes the data.
    cv_analyzer: DataAnalyzer = DataAnalyzer(_data_dir / "DATA", logger=_logger)
    cv_analyzer.analyze_data(
        sample_name="K4[Fe(CN)6]",
        experiment_name="CV_Multi_ScanRate",
        technique="CV",
        analysis_settings={
            "Plot": {"title": f"{sample_name} CV_Multi_ScanRate"},
            "Peak Picking": {},
            "Integration": {},
            "Peaks Scanrate": {}
        },
        raw_data=results
    )

    _logger.stop_gui()


if __name__ == "__main__":

    parent_dir = Path(__file__).parent
    with open(parent_dir / "test_settings" / "file_settings") as file:
        data_dir = Path(file.read())

    print(f"{parent_dir=}")
    sample_name = Sample_Name

    logger = GraphicalInterface(
        logging_config=parent_dir / "test_settings" / "logger_settings.json",
        log_file=data_dir / "Logs" / f"{timestamp_datetime()}_{sample_name}_CV_multi_scan_rate.log",
        disable_gui=False,
    )
    logger.sample_name = sample_name
    logger.info(f"Starting Experiment: CV scans of {logger.sample_name} at Various Scan Rates.")

    worker_thread = ThreadWithReturn(target=go_measurement(_data_dir=data_dir, _parent_dir=parent_dir, _logger=logger))
    worker_thread.start()
    logger.start_gui()
    worker_thread.join()

