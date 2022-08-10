from pathlib import Path

from HardwareController import SamplingSystem
from Utils import get_logger, timestamp_datetime


PARENT_DIR = Path(__file__).parent

logger = get_logger(
    config_file=PARENT_DIR / "test_settings" / "logger_settings.json",
    logger_name="EChem",
    logfile=Path(f"Test_Sampling_System_{timestamp_datetime()}.log")
)

sampler = SamplingSystem(
    config_file=PARENT_DIR / "test_settings" / "sampler_settings.json",
    logger=logger,
    initial_wash=0
)

sampler.disconnect()

"""
# Transfers 1.0 mL from autosampler position 1 to the cell

sampler.transfer_to_cell(
    source_port=1,
    volume=1.0,
    wash_line=True
)


# Washes the cell with 3 x 5 mL washing solvent

sampler.wash_cell(
    wash_volume=5.0,
    cycles=1
)
"""