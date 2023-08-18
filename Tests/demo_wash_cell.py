from pathlib import Path

from etoad.HardwareController import SamplingSystem
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime

"""
This Script is created to wash the EChem Cell in case an experiment was interrupted.
"""

# ========== Sample Settings Below ========== #

Disable_GUI: bool = True        # We are disabling GUI for simple cell washing.
REPEAT: int = 3                 # How many times the cell will be washed.
WASH_VOLUME = 5.0               # Wash volume each time

# ========== Sample Settings Above ========== #


def wash_cell(disable_gui=Disable_GUI, repeat=REPEAT, wash_volume=WASH_VOLUME):

    parent_dir = Path(__file__).parent
    with open(parent_dir / "test_settings" / "file_settings") as file:
        data_dir = Path(file.read())

    logger = GraphicalInterface(
        logging_config=parent_dir / "test_settings" / "logger_settings.json",
        log_file=data_dir / "logs" / f"{timestamp_datetime()}_wash_echem_cell.log",
        disable_gui=disable_gui
    )

    sampler = SamplingSystem(
        config_file=parent_dir / "test_settings" / "sampler_settings.json",
        logger=logger,
        pump_wash=0,
        cell_filled=True
    )

    sampler.wash_cell(repeat)
    sampler.transfer_to_cell(source_port=12, volume=wash_volume, wash_line=True)


if __name__ == "__main__":
    wash_cell()

