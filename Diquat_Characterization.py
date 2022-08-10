from pathlib import Path

from WorkflowManager import WorkflowManager
from Utils import timestamp_datetime
from Utils.DropboxPath import get_dropbox_path

data_dir = get_dropbox_path() / "PythonScript" / "EChem"

manager: WorkflowManager = WorkflowManager(
    logger_settings=data_dir / "Settings" / "logger_settings.json",
    logfile=data_dir / "Data" / f"Diquat_Characterization_{timestamp_datetime()}.log",
    potentiostat_settings=data_dir / "Settings" / "potentiostat_settings.json",
    sampler_settings=data_dir / "Settings" / "sampler_settings.json",
    data_path=data_dir / "Data"
)

samples: dict = {
    # "C3Br2": 3,
    "C2Br2-6NMePh": 4,
    "C2Br2-5,5-NMePh": 5,
    "C2Br2-5,5-DPA": 6
}

for sample in samples:
    manager.measure_sample(
        sample_name=sample,
        sample_location=samples[sample],
        workflow_path=Path("diquat_characterization.json")
    )

manager.shutdown_system()
