from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from HardwareController.Potentiostat.EChemController import EChemController
from Utils import get_logger, timestamp_datetime


PARENT_DIR = Path(__file__).parent

logger = get_logger(
    config_file=PARENT_DIR / "test_settings" / "logger_settings.json",
    logger_name="EChem",
    logfile=Path(f"Test_Potentiostat_{timestamp_datetime()}.log")
)


potentiostat = EChemController(
    config_file=PARENT_DIR / "test_settings" / "potentiostat_settings.json",
    logger=logger,
    simulation_mode=False
)



# Performs a Square Wave Voltammetry Measurement with Default Parameters

results: np.ndarray = potentiostat.do_measurement(
    technique="CV",
    set_parameters={
        "TechniqueParameters": {
            "Voltage Profile": {
                "value": [0, 0, -0.5, 0, 0]
            }
        },
        "Scan Rate": {
            "changed_over_iterations": True,
            "value": [
                [0.05, 0.05, 0.05, 0.05, 0.05],
                [0.1, 0.1, 0.1, 0.1, 0.1],
                [0.2, 0.2, 0.2, 0.2, 0.2]
            ]
        },
        "Number of Cycles": {
            "value": 2
        }
    }
)

potentiostat.disconnect()

plt.plot(results[:, 1], results[:, 2])
plt.show()
print("yey")
plt.close()

"""
# Performs a Cyclic Voltammetry Measurement (10 Cycles between 0 and -0.5 V)

potentiostat.load_technique(
    technique="CV",
    set_parameters={
        "Voltage Profile": [0.5, 0.5, -0.5, 0.5, 0.5],
        "Number of Cycles": 5
    }
)

results: np.ndarray = potentiostat.do_measurement()

plt.scatter(results[:, 1], results[:, 2])
plt.show()
"""