from pathlib import Path

from etoad.HardwareController import SamplingSystem
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime, get_dropbox_path

PARENT_DIR = get_dropbox_path() / "PythonScript" / "EChem" / "Settings"

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "logger_settings.json",
    log_file=PARENT_DIR / "logs" / f"{timestamp_datetime()}_wash_echem_cell.log"
)

sampler = SamplingSystem(
    config_file=PARENT_DIR / "sampler_settings.json",
    logger=logger,
    initial_wash=0,
    cell_filled=True
)

sampler.wash_cell(3)
sampler.transfer_to_cell(source_port=12,volume=5, wash_line=True)
