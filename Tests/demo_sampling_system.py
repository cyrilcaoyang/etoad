from pathlib import Path

from src.etoad.HardwareController import SamplingSystem
from src.etoad.Utils import timestamp_datetime
from src.etoad.Interface import GraphicalInterface

"""
    This python script demonstrate the Sampling System.
"""

# ========== Test Settings Below ========== #

Sample_Name = "K4[Fe(CN)6]"     # Name of the Chemical Solution
Source_Port = 9                 # The Port from which the Sample will be added.
Sample_Vol = 0.5                # The volume of sample in mL (< 5mL) to be diluted to 5 mL in the Cell.

Clean_Up: bool = False          # Cleaning Up the EChem Reactor by washing the cell with 3 x 5 mL Solvent.
Disable_GUI: bool = True        # We are disabling GUI for simple liquid transfer.

# ========== Test Settings Above ========== #

PARENT_DIR = Path(__file__).parent
with open(PARENT_DIR / "test_settings" / "file_settings") as file:
    DATA_DIR = Path(file.read())

# We are not using GUI for simple liquid transfer
logger = GraphicalInterface(
    logging_config=PARENT_DIR / "test_settings" / "logger_settings.json",
    log_file=DATA_DIR / "Logs" / f"{timestamp_datetime()}_{Sample_Name}_transfer_dilution.log",
    disable_gui=Disable_GUI
)

# The EChem Reactor is filled with electrolyte solution by default.
sampler = SamplingSystem(
    config_file=PARENT_DIR / "test_settings" / "sampler_settings.json",
    logger=logger,
    pump_wash=0,
    cell_filled=True
)

# Transfers 0.5 mL from the sample position 9 to the cell
sampler.transfer_to_cell(
    source_port=Source_Port,
    volume=Sample_Vol,
    wash_line=True
)

sampler.dilute_cell(volume=5)

if Clean_Up:
    sampler.wash_cell(
         wash_volume=5.0,
         cycles=3
    )

sampler.disconnect()
