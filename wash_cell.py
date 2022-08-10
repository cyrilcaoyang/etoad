from pathlib import Path

from HardwareController import SamplingSystem
from Utils import get_logger
from Utils.DropboxPath import get_dropbox_path

echem_path: Path = get_dropbox_path() / "PythonScript" / "EChem"

logger = get_logger(
    config_file=echem_path / "Settings" / "logger_settings.json",
    logger_name="EChem"
)

sampler = SamplingSystem(
    config_file=echem_path / "Settings" / "sampler_settings.json",
    logger=logger,
    initial_wash=0
)

sampler._cell_volume = 5

for position in range(1, 7):
    sampler.wash_autosampler_position(position)

sampler.wash_cell(
    wash_volume=5.0,
    cycles=3
)

sampler.dilute_cell(volume=5)