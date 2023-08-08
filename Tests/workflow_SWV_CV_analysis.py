import os
from pathlib import Path

from etoad import WorkflowManager
from etoad.Utils import timestamp_datetime

# Executes the workflow in the following steps using a GUI (which can be turned off):
#   - Sample transfer to the measurement cell
#   - Square Wave Voltammetry measurement
#   - Cyclic Voltammetry measurement based on parameters inferred from the SWV measurement
#   - Data analysis, visualization and storage
#   - Cell cleaning after the measurements

#   {"sample_name": "K4[Fe(CN)6]", "sample_location": 9, "workflow_path": Path("test_stability_pos.json")}
#                    ^^^^^^^^^^^                      ^                         ^^^^^^^^^^^^^^^^^^^^^^^^
#                 name of the sample          position of the vial              settings of the workflow

# ========== Submit Samples Below ========== #

Job_Queue = [
    {"sample_name": "K4[Fe(CN)6]", "sample_location": 9, "workflow_path": Path("workflow_stability_pos.json")},
    # {"sample_name": "Fe-ligand184-1", "sample_location": 1, "workflow_path": Path("")},
    # {"sample_name": "Fe-ligand184-2", "sample_location": 2, "workflow_path": Path("")}
    # {"sample_name": "CYR-181", "sample_location": 3, "workflow_path": Path("")},
    # {"sample_name": "wash", "sample_location": 4, "workflow_path": Path("")},
    {"sample_name": "diquat-44Me-C2Br2", "sample_location": 5, "workflow_path": Path("workflow_stability_neg.json")},
    # {"sample_name": "wash", "sample_location": 6, "workflow_path": Path("")},
    # {"sample_name": "wash", "sample_location": 7, "workflow_path": Path("")},
    # {"sample_name": "Fe-bpy-44CH2TMABr", "sample_location": 8, "workflow_path": Path("")}
]

# ========== Submit Samples Above ========== #

PARENT_DIR = Path(__file__).parent
with open(PARENT_DIR / "test_settings" / "file_settings") as file:
    if os.path.exists(file):
        DATA_DIR = Path(file.read())
    else: raise FileExistsError

manager: WorkflowManager = WorkflowManager(
    logger_settings=PARENT_DIR / "test_settings" / "logger_settings.json",
    logfile=Path(DATA_DIR / "Logs" / f"{timestamp_datetime()}_workflow_manager.log"),
    potentiostat_settings=PARENT_DIR / "test_settings" / "potentiostat_settings.json",
    sampler_settings=PARENT_DIR / "test_settings" / "sampler_settings.json",
    data_path=Path(DATA_DIR / "DATA"),
    disable_gui=False
)

manager.submit_samples(Job_Queue)
manager.start_system()

# TODO: come up with a way to skip current run, save data, and go to the next job
# test DPV-OCV-CV: after negative square wave, time.sleep for 30 sec and start CV from OCV
# change initial port to WASTE
# also document firmware version on the potentiostat
