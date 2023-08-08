import threading
import numpy
from pathlib import Path

from etoad.HardwareController.Potentiostat.EChemController import EChemController
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime, get_dropbox_path

# ========== Sample Settings Below ========== #

Sample_Name = "K4[Fe(CN)6]"
V_init = 1.4            # Unit: Initial Voltage in V
V_fin = 0               # Unit: Final Voltage in V
T_rest = 10             # The Resting Time Before the Scan

Disable_GUI: bool = False
Simulation: bool = False

# ========== Sample Settings Above ========== #

PARENT_DIR = Path(__file__).parent
with open(PARENT_DIR / "test_settings" / "file_settings") as file:
    DATA_DIR = Path(file.read())

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "test_settings" / "logger_settings.json",
    log_file=DATA_DIR / "Logs" / f"{timestamp_datetime()}_simple_SWV.log",
    disable_gui=Disable_GUI
)


def do_measurement():

    potentiostat = EChemController(
        config_file=PARENT_DIR / "test_settings" / "potentiostat_settings.json",
        logger=logger,
        simulation_mode=Simulation,
    )

    logger.sample_name = Sample_Name
    logger.info(f"*** Starting Experiment: SWV Scan of {logger.sample_name}.")

    results = potentiostat.do_measurement(
        technique="SWV",
        set_parameters={
            "IterationSettings": {
                "no_iterations": 1
            },
            "TechniqueParameters": {
                "Initial Voltage": {"value": V_init},
                "Rest Time": {"value": T_rest},
                "Final Voltage": {"value": V_fin},
            }
        }
    )

    # saving the data before disconnection
    filename = DATA_DIR / "Data" / f"SWV_test_{logger.sample_name}_{timestamp_datetime()}.csv"
    numpy.savetxt(filename, results, delimiter=',')
    potentiostat.disconnect()
    logger.stop_gui()


worker_thread = threading.Thread(target=do_measurement)
worker_thread.start()
logger.start_gui()
worker_thread.join()


