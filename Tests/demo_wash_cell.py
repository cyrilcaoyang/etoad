from pathlib import Path

from etoad.HardwareController import SamplingSystem
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime

"""
This Script is created to wash the EChem Cell in case an experiment was interrupted.
"""

# ========== Sample Settings Below ========== #

Disable_GUI: bool = True        # We are disabling GUI for simple cell washing.

# ========== Sample Settings Above ========== #

PARENT_DIR = Path(__file__).parent
with open(PARENT_DIR / "test_settings" / "file_settings") as file:
    DATA_DIR = Path(file.read())

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "test_settings" / "logger_settings.json",
    log_file=DATA_DIR / "logs" / f"{timestamp_datetime()}_wash_echem_cell.log",
    disable_gui=Disable_GUI
)

sampler = SamplingSystem(
    config_file=PARENT_DIR / "test_settings" / "sampler_settings.json",
    logger=logger,
    pump_wash=0,
    cell_filled=True
)

sampler.wash_cell(3)
sampler.transfer_to_cell(source_port=12, volume=5, wash_line=True)
