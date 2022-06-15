from pathlib import Path
import numpy as np

# Import the Controller for the Potentiostat and some Helper Functions
from Potentiostat import EChemController
from Utils import get_logger
from Utils.PreliminaryDataHandling import scatter_plot, save_data

# Definition of Global Variables (PRELIMINARY!)
POTENTIOSTAT_CONFIG = Path("Settings/potentiostat_settings.json")
LOGGER_CONFIG = Path("Settings/logger_settings.json")
DATA_PATH = Path(r"C:\Users\Potentiostat_SP-300\Desktop\AutoEChem_Data")

sample_name: str = "Test"
technique: str = "SWV"
parameters: dict = {}

# Instantiation of the Logger and Controller Objects.
logger = get_logger(
    config_file=LOGGER_CONFIG,
    logger_name="EChem"
)

controller = EChemController(
    config_file=POTENTIOSTAT_CONFIG,
    logger=logger
)

# Performance of all Measurements (Load Technique, Measure, Plot Results, Save Results)

logger.info(f"Starting Experiment for Compound {sample_name}")

controller.load_technique(
    technique=technique,
    set_parameters=parameters
)

results: np.ndarray = controller.do_measurement()

scatter_plot(
    results[:, 1],
    results[:, 2],
    show=False,
    save=True,
    file_name=DATA_PATH / f"{sample_name}_{technique}.png"
)

save_data(
    results,
    file_name=DATA_PATH / f"{sample_name}_{technique}.pkl"
)

logger.debug(f"Data for Compound {sample_name} saved to {sample_name}_{technique}.pkl")
