from pathlib import Path

from WorkflowManager import WorkflowManager
from Utils import timestamp_datetime
from Utils.DropboxPath import get_dropbox_path

settings_dir = get_dropbox_path() / "PythonScript" / "EChem"
file_name = Path(__file__).stem
data_dir = Path(r"C:\Users\Potentiostat_SP-300\Desktop\AutoEChem_Data")

manager: WorkflowManager = WorkflowManager(
    logger_settings=settings_dir / "Settings" / "logger_settings_v2.json",
    logfile=settings_dir / "Data" / f"{file_name}_{timestamp_datetime()}.log",
    potentiostat_settings=settings_dir / "Settings" / "potentiostat_settings.json",
    sampler_settings=settings_dir / "Settings" / "sampler_settings.json",
    data_path=data_dir
)

# Sets a couple of frequently used routines as variables
NEG_POTENTIAL_STABILITY = Path("routine_neg_potential_stability.json")
POS_POTENTIAL_STABILITY = Path("routine_pos_potential_stability.json")
REFERENCE = Path("routine_reference.json")
SIMPLE_SWV_SCANS = Path("routine_simple_SWVscans.json")


# Defines the sample names, locations and variables to specify the right routine
samples: list = [
    {"sample_name": "C2Br2-55NMePh ACN", "sample_location": 1, "workflow_path": NEG_POTENTIAL_STABILITY},
    {"sample_name": "C2BF4-55NMePh in ACN", "sample_location": 2, "workflow_path": NEG_POTENTIAL_STABILITY},
    {"sample_name": "C3Br2-55NMePh in ACN", "sample_location": 3, "workflow_path": NEG_POTENTIAL_STABILITY},
    {"sample_name": "C3Br2-33Me in water", "sample_location": 7, "workflow_path": NEG_POTENTIAL_STABILITY},
    {"sample_name": "C3Br2-Aza in water", "sample_location": 8, "workflow_path": NEG_POTENTIAL_STABILITY},
    {"sample_name": "K4FeCN6 in water", "sample_location": 9, "workflow_path": REFERENCE},
]

# Submit the samples to the WorkflowManager, and start the measurements
manager.submit_samples(samples)
results = manager.start_system()

