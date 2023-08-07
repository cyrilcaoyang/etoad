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
Cycle_Numbers: int = 3    # The Numer of Cycles at each Scan Rate

Scan_Rates = [0.050, 0.100, 0.200, 0.400, 1.000]    # Unit: Scan Rate in V/s
# Example  = [0.050, 0.100, 0.200, 0.400, 1.000]

Disable_GUI: bool = False
Simulation: bool = False

# ========== Sample Settings Above ========== #

"""
Demonstration of Iterations of CV scans with various scan rates. 
"""

PARENT_DIR = get_dropbox_path() / "PythonScript" / "EChem"

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "Settings" / "logger_settings.json",
    log_file=PARENT_DIR / "Logs" / f"{timestamp_datetime()}_CV_multi_scan_rate.log",
    disable_gui=False
)

Num_Iter = len(Scan_Rates)
list_scan_rates = [[Scan_Rates[i] for _ in range(5)] for i in range(Num_Iter)]
print(Num_Iter)
print(Scan_Rates)


def do_measurement():

    potentiostat = EChemController(
        config_file=PARENT_DIR / "Settings" / "potentiostat_settings.json",
        logger=logger,
        simulation_mode=False,
    )

    # logger.sample_name = ""
    logger.sample_name = "K4[Fe(CN)6]"
    logger.info(f"*** Starting Experiment: CV scans of {logger.sample_name} at Various Scan Rates.")

    results = potentiostat.do_measurement(
        technique="CV",
        set_parameters={
            "IterationSettings": {
                "no_iterations": Num_Iter
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
    filename = PARENT_DIR.parent / "Data" / f"CV_Multi_ScanRate_{logger.sample_name}_{timestamp_datetime()}.csv"
    numpy.savetxt(filename, results, delimiter=',')
    logger.info(f"<<< Result of CV scans of {logger.sample_name} is saved as {filename}.")
    potentiostat.disconnect()
    logger.stop_gui()


worker_thread = threading.Thread(target=do_measurement)
worker_thread.start()
logger.start_gui()
worker_thread.join()

# TODO: Add Analysis of results, and Plots
