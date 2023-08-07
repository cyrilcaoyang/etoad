from src.etoad.HardwareController import SamplingSystem
from src.etoad.Utils import timestamp_datetime, get_dropbox_path
from src.etoad.Interface import GraphicalInterface

# ========== Sample Settings Below ========== #

Sample_Name = "K4[Fe(CN)6]"     # Name of the Chemical Solution
Source_Port = 9                 # The Port from which the Sample will be added.

Clean_Up: bool = False          # Cleaning Up the EChem Reactor afterwards.

Disable_GUI: bool = True        # We are disabling GUI for simple liquid transfer.
Simulation: bool = False

# ========== Sample Settings Above ========== #

PARENT_DIR = get_dropbox_path() / "PythonScript" / "EChem"

# We are not using GUI for simple liquid transfer
logger = GraphicalInterface(
    logging_config=PARENT_DIR / "Settings" / "logger_settings.json",
    log_file=PARENT_DIR / "Logs" / f"{timestamp_datetime()}_test_Sampling_System.log",
    disable_gui=Disable_GUI
)

# The EChem Reactor is filled with electrolyte solution by default.
sampler = SamplingSystem(
    config_file=PARENT_DIR / "Settings" / "sampler_settings.json",
    logger=logger,
    initial_wash=0,
    cell_filled=True
)

# Transfers 0.5 mL from the sample position 9 to the cell
sampler.transfer_to_cell(
    source_port=Source_Port,
    volume=0.5,
    wash_line=True
)

sampler.dilute_cell(volume=5)

# Washes the cell with 3 x 5 mL washing solvent

if Clean_Up:
    sampler.wash_cell(
         wash_volume=5.0,
         cycles=3
    )

sampler.disconnect()
