from pathlib import Path

from src.etoad.HardwareController import SamplingSystem
from src.etoad.Interface import GraphicalInterface
from src.etoad.Utils.DropboxPath import get_dropbox_path

PARENT_DIR: Path = get_dropbox_path() / "PythonScript" / "EChem"
# computer-dependent path

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "Settings" / "logger_settings_v2.json"
)

sampler = SamplingSystem(
    config_file=PARENT_DIR / "Settings" / "sampler_settings.json",
    logger=logger,
    initial_wash=0,
    cell_filled=True
)

sampler.wash_cell(2)
