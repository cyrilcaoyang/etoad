import threading
import numpy

from etoad.HardwareController.Potentiostat.EChemController import EChemController
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime, get_dropbox_path

"""
Demonstration of Iterations of CV scans with various scan rates. 
"""

PARENT_DIR = get_dropbox_path() / "PythonScript" / "EChem" / "Settings"

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "logger_settings_v2.json",
    log_file=PARENT_DIR / "logs" / f"Test_Potentiostat_{timestamp_datetime()}.log",
    disable_gui=False
)


def do_measurement():

    potentiostat = EChemController(
        config_file=PARENT_DIR / "potentiostat_settings.json",
        logger=logger,
        simulation_mode=False,
    )

    logger.sample_name = "K4[Fe(CN)6]"
    # logger.sample_name = ""

    results = potentiostat.do_measurement(
        technique="CV",
        set_parameters={
            "IterationSettings": {
                "no_iterations": 3
            },
            "TechniqueParameters": {
                "Voltage Profile": {
                    "value": [0.0, 0.0, 0.5, 0.0, 0.0]
                },
                "Scan Rate": {
                    "changed_over_iterations": True,
                    "value": [
                        [0.05, 0.05, 0.05, 0.05, 0.05],
                        [0.10, 0.10, 0.10, 0.10, 0.10],
                        [0.20, 0.20, 0.20, 0.20, 0.20],
                    ]
                },
                "Number of Cycles": {
                    "value": 5
                }
            }
        }
    )

    # saving the data before disconnection
    filename = PARENT_DIR.parent / "Data" / f"CV_test_{logger.sample_name}_{timestamp_datetime()}.csv"
    numpy.savetxt(filename, results, delimiter=',')
    logger.info(f"Result of CV scans of {logger.sample_name} is saved.")
    potentiostat.disconnect()
    logger.stop_gui()


worker_thread = threading.Thread(target=do_measurement)
logger.info(f"Starting CV scans of {logger.sample_name}.")
worker_thread.start()
logger.start_gui()
worker_thread.join()


