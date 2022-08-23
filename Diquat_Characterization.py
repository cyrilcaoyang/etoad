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
    # "K4FeCN6-start": 9,
    # "C3I2-6Br": 1,
    # "C3Br2-6NMePh": 2,
    "C3Br2-55NMePh": 3,
    "C3Br2-2TPA": 4,
    "K4FeCN6-mid": 9,
    # "C2Br2-55NMePh": 5,
    "C3Br2-Aza": 6,
    "C2Br2-Aza": 7,
    # "C3Br2-44NH2": 8,
    # "K4FeCN6-end": 9
}


# Choose the right json file that defines the experimental routine

for sample in samples:
    manager.measure_sample(
        sample_name=sample,
        sample_location=samples[sample],
        workflow_path=Path("routine_simple_scans.json")
    )

manager.shutdown_system()
