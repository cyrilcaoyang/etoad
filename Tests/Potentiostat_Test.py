from pathlib import Path

from HardwareController.Potentiostat.EChemController import EChemController
from Interface import GraphicalInterface
from Utils import timestamp_datetime


PARENT_DIR = Path(__file__).parent

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "test_settings" / "logger_settings_v2.json",
    log_file=Path(f"Test_Potentiostat_{timestamp_datetime()}.log")
)


potentiostat = EChemController(
    config_file=PARENT_DIR / "test_settings" / "potentiostat_settings.json",
    logger=logger
)

potentiostat.load_technique(
    technique="SWV",
    set_parameters={
        "Initial Voltage": -0.5,
        "Final Voltage": 0.8,
    }
)

results = potentiostat.do_measurement()

potentiostat.disconnect()
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