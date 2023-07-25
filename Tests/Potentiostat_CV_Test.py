import threading
from pathlib import Path

import numpy

from src.etoad.HardwareController.Potentiostat.EChemController import EChemController
from src.etoad.Interface import GraphicalInterface
from src.etoad.Utils import timestamp_datetime, get_dropbox_path

PARENT_DIR = get_dropbox_path() / "PythonScript" / "EChem" / "Settings"

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "logger_settings_v2.json",
    log_file=PARENT_DIR / "logs" / f"Test_Potentiostat_{timestamp_datetime()}.log"
)


def do_measurement():

    potentiostat = EChemController(
        config_file=PARENT_DIR / "potentiostat_settings.json",
        logger=logger,
        simulation_mode=False,
    )

    # logger.sample_name = "K4[Fe(CN)6]"
    logger.sample_name = "Fe-bpy4Me4COONa"

    results = potentiostat.do_measurement(
        technique="CV",
        set_parameters={
            "IterationSettings": {
                "no_iterations": 1
            },
            "TechniqueParameters": {
                "Voltage Profile": {
                    "value": [0.6, 0.6, 0.90, 0.6, 0.6]
                },
                "Scan Rate": {
                    "value": [0.10, 0.10, 0.10, 0.10, 0.10]
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
    potentiostat.disconnect()
    logger.stop_gui()


worker_thread = threading.Thread(target=do_measurement)
worker_thread.start()
logger.start_gui()
worker_thread.join()


