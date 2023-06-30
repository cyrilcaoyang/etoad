import time

from src.etoad.HardwareController.SamplingSystem import Hotplate
from src.etoad.Utils import timestamp_datetime, get_dropbox_path
from src.etoad.Interface import GraphicalInterface
from logging import Logger

PARENT_DIR = get_dropbox_path() / "PythonScript" / "EChem" / "Settings"

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "logger_settings_v2.json",
    log_file=PARENT_DIR / "logs" / f"Hotplate_Tests_{timestamp_datetime()}.log"
)

port = 'COM5'
plate = Hotplate.Hotplate(device_port=port)
plate.start_stirring()
logger.info("Started stirring.")

plate.target_stir_rate = 100
time.sleep(10)
logger.info("Stirring at 100 rpm.")

plate.target_stir_rate = 200
plate.stop_stirring()
logger.info("Stirring at 200 rpm.")

plate.target_temperature = 20
plate.start_heating()
logger.info("Heating to 20C.")

plate.target_temperature = 19
logger.info("Heating to 30C.")
time.sleep(5)

plate.stop_heating()
plate.disconnect()

