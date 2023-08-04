from pathlib import Path

from src.etoad.HardwareController import SamplingSystem
from src.etoad.Utils import timestamp_datetime, get_dropbox_path
from src.etoad.Interface import GraphicalInterface


PARENT_DIR = get_dropbox_path() / "PythonScript" / "EChem" / "Settings"

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "logger_settings_v2.json",
    log_file=PARENT_DIR / "logs" / f"Test_Sampling_System_{timestamp_datetime()}.log"
)

sampler = SamplingSystem(
    config_file=PARENT_DIR / "sampler_settings.json",
    logger=logger,
    initial_wash=0,
    cell_filled=True
)

# Transfers 0.5 mL from the autosampler position 9 to the cell
sampler.transfer_to_cell(
    source_port=9,
    volume=0.5,
    wash_line=True
)

sampler.dilute_cell(volume=5)

# Washes the cell with 3 x 5 mL washing solvent
#
# sampler.wash_cell(
#     wash_volume=5.0,
#     cycles=1
#

sampler.disconnect()
