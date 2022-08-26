from pathlib import Path

from WorkflowManager import WorkflowManager
from Utils import timestamp_datetime
from Utils.DropboxPath import get_dropbox_path

data_dir = get_dropbox_path() / "PythonScript" / "EChem"
file_name = Path(__file__).stem

manager: WorkflowManager = WorkflowManager(
    logger_settings=data_dir / "Settings" / "logger_settings.json",
    logfile=data_dir / "Data" / f"{file_name}_{timestamp_datetime()}.log",
    potentiostat_settings=data_dir / "Settings" / "potentiostat_settings.json",
    sampler_settings=data_dir / "Settings" / "sampler_settings.json",
    data_path=Path(r"C:\Users\Potentiostat_SP-300\Desktop\AutoEChem_Data")
)


# Defines the sample names and locations

samples: dict = {
    # "C2Br2-55NMePh ACN": 1,
    # "C2BF4-55NMePh in ACN": 2,
    # "C3Br2-55NMePh in ACN": 3,
    "C3Br2-33Me in water": 7,
    # "C3Br2-Aza in water": 8,
    # "K4FeCN6 in water": 9
}


# Choose the right json file that defines the experimental routine

for sample in samples:
    manager.measure_sample(
        sample_name=sample,
        sample_location=samples[sample],
        workflow_path=Path("routine_neg_potential_stability.json")
    )

manager.shutdown_system()
