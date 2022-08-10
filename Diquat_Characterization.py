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
    data_path=data_dir / "Data"
)

samples: dict = {
    "C2Br2-6NMePh": 1,
    "C3Br2-4,4-DPA": 2
}

manager.measure_sample(
    sample_name="K2[Fe(CN)6]",
    sample_location=9,
    workflow_path=Path("reference.json")
)

manager.shutdown_system()
