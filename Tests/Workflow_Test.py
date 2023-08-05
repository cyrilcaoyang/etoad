from pathlib import Path

from etoad import WorkflowManager
from etoad.Utils import timestamp_datetime, get_dropbox_path

PARENT_DIR = Path(__file__).parent
DROPBOX_DIR = get_dropbox_path() / "PythonScript" / "EChem"

manager: WorkflowManager = WorkflowManager(
    logger_settings=PARENT_DIR / "test_settings" / "logger_settings.json",
    logfile=Path(DROPBOX_DIR / "Logs" / f"Test_Workflow_Manager_{timestamp_datetime()}.log"),
    potentiostat_settings=PARENT_DIR / "test_settings" / "potentiostat_settings.json",
    sampler_settings=PARENT_DIR / "test_settings" / "sampler_settings.json",
    data_path=Path(DROPBOX_DIR / "AutoEChem_Data"),
    disable_gui=False
)

# Executes the workflow specified in test_workflow.json for a test sample on the autosampler (position 1).
# The workflow contains the following steps:
#   - Sample transfer to the measurement cell
#   - Square Wave Voltammetry measurement
#   - Cyclic Voltammetry measurement based on parameters inferred from the SWV measurement
#   - Data analysis, visualization and storage
#   - Cell cleaning after the measurements

manager.submit_samples([
    {"sample_name": "K4[Fe(CN)6]", "sample_location": 9, "workflow_path": Path("test_stability_pos.json")}
    # {"sample_name": "Fe-ligand184-1", "sample_location": 1, "workflow_path": Path("test_stability_pos.json")},
    # {"sample_name": "Fe-ligand184-2", "sample_location": 2, "workflow_path": Path("test_stability_pos.json")}
    # {"sample_name": "CYR-181", "sample_location": 3, "workflow_path": Path("test_stability_neg.json")},
    # {"sample_name": "wash", "sample_location": 4, "workflow_path": Path("wash_vials.json")},
    # {"sample_name": "diquat-44Me-C2Br2", "sample_location": 5, "workflow_path": Path("test_stability_neg.json")},
    # {"sample_name": "wash", "sample_location": 6, "workflow_path": Path('wash_vials.json')}
    # {"sample_name": "wash", "sample_location": 7, "workflow_path": Path("wash_vials.json")},
    # {"sample_name": "Fe-bpy-44CH2TMABr", "sample_location": 8, "workflow_path": Path("test_stability_pos.json")}
    # {"sample_name": "K4[Fe(CN)6]", "sample_location": 9, "workflow_path": Path("test_stability_pos.json")}
])

manager.start_system()

# TODO: come up with a way to skip current run, save data, and go to the next job
# TODO: test DPV-OCV-CV: after negative square wave, time.sleep for 30 sec and start CV from OCV
# TODO: change initial port to WASTE
# TODO: also document firmware version on the potentiostat
