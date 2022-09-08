import threading
from pathlib import Path

from HardwareController.Potentiostat.EChemController import EChemController
from Interface import GraphicalInterface
from Utils import timestamp_datetime, get_dropbox_path


PARENT_DIR = get_dropbox_path() / "PythonScript" / "EChem" / "Settings"

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "logger_settings_v2.json",
    log_file=Path(f"Test_Potentiostat_{timestamp_datetime()}.log")
)


def do_measurement():

    potentiostat = EChemController(
        config_file=PARENT_DIR / "potentiostat_settings.json",
        logger=logger
    )

    logger.sample_name = "K4[Fe(CN)6]"

    potentiostat.load_technique(
        technique="SWV",
        set_parameters={
            "Initial Voltage": -0.5,
            "Final Voltage": 0.8,
        }
    )
    results = potentiostat.do_measurement()

    potentiostat.disconnect()
    # logger.stop_gui()


threading.Thread(target=do_measurement).start()
logger.start_gui()

"""
# Performs a Cyclic Voltammetry Measurement (5 Cycles between 0.5 and -0.5 V)

potentiostat.load_technique(
    technique="CV",
    set_parameters={
        "Voltage Profile": [0.5, 0.5, -0.5, 0.5, 0.5],
        "Number of Cycles": 5
    }
)

results: np.ndarray = potentiostat.do_measurement()

potentiostat.disconnect()
"""