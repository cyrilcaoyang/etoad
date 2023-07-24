from pathlib import Path

from src.etoad import WorkflowManager
from src.etoad.Utils import timestamp_datetime

PARENT_DIR = Path(__file__).parent

manager: WorkflowManager = WorkflowManager(
    logger_settings=PARENT_DIR / "test_settings" / "logger_settings.json",
    logfile=Path(PARENT_DIR / "log_files" / f"Test_Workflow_Manager_{timestamp_datetime()}.log"),
    potentiostat_settings=PARENT_DIR / "test_settings" / "potentiostat_settings.json",
    sampler_settings=PARENT_DIR / "test_settings" / "sampler_settings.json",
    data_path=Path(r"C:\Users\Potentiostat_SP-300\Desktop\AutoEChem_Data")
)

# Executes the workflow specified in test_workflow.json for a test sample on the autosampler (position 1).
# The workflow contains the following steps:
#   - Sample transfer to the measurement cell
#   - Square Wave Voltammetry measurement
#   - Cyclic Voltammetry measurement based on parameters inferred from the SWV measurement
#   - Data analysis, visualization and storage
#   - Cell cleaning after the measurements

manager.submit_samples([
    # {"sample_name": "transquat-C2Cl2", "sample_location": 2, "workflow_path": Path("test_stability_negative.json")},
    # {"sample_name": "diquat-C2C2Br2", "sample_location": 1, "workflow_path": Path("test_stability_negative.json")}
    # {"sample_name": "CYR-181", "sample_location": 3, "workflow_path": Path("test_stability_negative.json")},
    # {"sample_name": "wash", "sample_location": 4, "workflow_path": Path("wash_vials.json")},
    # {"sample_name": "diquat-44Me-C2Br2", "sample_location": 5, "workflow_path": Path("test_stability_negative.json")}
    {"sample_name": "wash", "sample_location": 6, "workflow_path": Path('wash_vials.json')}
    # {"sample_name": "wash", "sample_location": 7, "workflow_path": Path("wash_vials.json")},
    # {"sample_name": "wash", "sample_location": 8, "workflow_path": Path("wash_vials.json")}
    # {"sample_name": "K4[Fe(CN)6]", "sample_location": 9, "workflow_path": Path("test_stability_routine.json")}
])

manager.start_system()

# TODO: Yang is there a way to skip current run and go to the next experiment/job
# TODO: Yang implement a way to find the dominant peak (integration) and ignor peaks less than 10% of the height
# TODO: After negative square wave, time.sleep for 30 sec so that voltage can recover
# initial wash always added vial to reaction although v=0 m/l???
# initial port always to WASTE
