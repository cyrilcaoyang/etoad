from pathlib import Path
import numpy as np

from HardwareController import EChemController
from Utils import get_logger, timestamp_datetime, scatter_plot


PARENT_DIR = Path(__file__).parent.parent

logger = get_logger(
    config_file=PARENT_DIR / "Settings" / "logger_settings.json",
    logger_name="EChem",
    logfile=Path(f"Test_Potentiostat_{timestamp_datetime()}.log")
)


potentiostat = EChemController(
    config_file=PARENT_DIR / "Settings" / "potentiostat_settings.json",
    logger=logger
)


# Performs a Square Wave Voltammetry Measurement with Default Parameters

potentiostat.load_technique(
    technique="SWV",
    set_parameters={}
)

results: np.ndarray = potentiostat.do_measurement()

scatter_plot(
    results[:, 1],
    results[:, 2],
)


# Performs a Cyclic Voltammetry Measurement (10 Cycles between 0 and -0.5 V)

potentiostat.load_technique(
    technique="CV",
    set_parameters={
        "Voltage Profile": [0, 0, -0.5, 0, 0],
        "Number of Cycles": 10
    }
)

results: np.ndarray = potentiostat.do_measurement()

scatter_plot(
    results[:, 1],
    results[:, 2],
)
