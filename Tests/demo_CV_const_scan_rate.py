import threading
import numpy

from etoad.HardwareController.Potentiostat.EChemController import EChemController
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime, get_dropbox_path

# ========== Sample Settings Below ========== #

Sample_Name = "K4[Fe(CN)6]"
V_init = 0                  # Unit: Initial Voltage in V
V_max = 0.5                 # Unit: Highest Voltage in V
V_min = 0                   # Unit: Lowest Voltage in V
V_fin = 0                   # Unit: Final Voltage in V
Scan_Rate = 0.050           # Unit: Scan Rate in V/s
Cycle_Numbers: int = 100    # The Numer of Cycles as an Integer

Disable_GUI: bool = False
Simulation: bool = False

# ========== Sample Settings Above ========== #

PARENT_DIR = get_dropbox_path() / "PythonScript" / "EChem"
logger = GraphicalInterface(
    logging_config=PARENT_DIR / "Settings" / "logger_settings.json",
    log_file=PARENT_DIR / "Logs" / f"{timestamp_datetime()}_CV_const_scan_rate.log",
    disable_gui=Disable_GUI
)


def do_measurement():
    potentiostat = EChemController(
        config_file=PARENT_DIR / "Settings" / "potentiostat_settings.json",
        logger=logger,
        simulation_mode=Simulation,
    )

    logger.sample_name = Sample_Name
    logger.info(f"*** Starting Experiment: CV Scans of {logger.sample_name}.")

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
    filename = PARENT_DIR.parent / "Data" / f"CV_Const_ScanRate_{logger.sample_name}_{timestamp_datetime()}.csv"
    numpy.savetxt(filename, results, delimiter=',')
    logger.info(f"<<< Result of CV scans of {logger.sample_name} is saved as {filename}.")
    potentiostat.disconnect()
    logger.stop_gui()


worker_thread = threading.Thread(target=do_measurement)
worker_thread.start()
logger.start_gui()
worker_thread.join()


