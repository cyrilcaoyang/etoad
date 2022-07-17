import time
from threading import Thread
from pathlib import Path

# Import the Controller for the Potentiostat and some Helper Functions
from HardwareController import EChemController
from Utils import get_logger
from Utils.PreliminaryDataHandling import scatter_plot, save_as_pkl

# Definition of Global Variables (PRELIMINARY!)
POTENTIOSTAT_CONFIG = Path("Settings/potentiostat_settings.json")
LOGGER_CONFIG = Path("Settings/logger_settings.json")
DATA_PATH = Path(r"C:\Users\Potentiostat_SP-300\Desktop\AutoEChem_Data")

technique: str = "SWV"
parameters: dict = {
}


logger = get_logger(
    config_file=LOGGER_CONFIG,
    logger_name="EChem",
    logfile=Path("TwoChannelTest.log")
)


POTENTIOSTAT = EChemController(
    config_file=POTENTIOSTAT_CONFIG,
    logger=logger
)


def measure(
        channel: int,
        technique_name: str,
        technique_parameters: dict,
        data_path: Path,
        sample_name: str
) -> None:
    """
    Early draft of a measurement function applicable to multi-threading.
    """
    POTENTIOSTAT.load_technique(technique_name, technique_parameters, channel)
    data = POTENTIOSTAT.do_measurement(channel)
    scatter_plot(data[:, 1], data[:, 2], show=False, save=True, file_name=data_path / f"{sample_name}.png")
    save_as_pkl(data, data_path / f"{sample_name}.pkl")


if __name__ == "__main__":

    process1 = Thread(target=measure, args=(0, technique, parameters, DATA_PATH, "Test_Channel_1"))
    process2 = Thread(target=measure, args=(1, technique, parameters, DATA_PATH, "Test_Channel_2"))

    process1.start()
    time.sleep(2)
    process2.start()
