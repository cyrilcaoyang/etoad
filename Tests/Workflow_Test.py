from pathlib import Path

from WorkflowManager import WorkflowManager
from Utils import timestamp_datetime


PARENT_DIR = Path(__file__).parent

manager: WorkflowManager = WorkflowManager(
    logger_settings=PARENT_DIR / "test_settings" / "logger_settings.json",
    logfile=Path(f"Test_Workflow_Manager_{timestamp_datetime()}.log"),
    potentiostat_settings=PARENT_DIR / "test_settings" / "potentiostat_settings.json",
    sampler_settings=PARENT_DIR / "test_settings" / "sampler_settings.json",
    data_path=Path(__file__).parent
)


# Executes the workflow specified in test_workflow.json for a test sample on the autosampler (position 1).
# The workflow contains the following steps:
#   - Sample transfer to the measurement cell
#   - Square Wave Voltammetry measurement
#   - Cyclic Voltammetry measurement based on parameters inferred from the SWV measurement
#   - Data analysis, visualization and storage
#   - Cell cleaning after the measurements

manager.measure_sample(
    sample_name="Test_Sample",
    sample_location=1,
    workflow_path=Path("test_workflow.json")
)

# TODO: provide a proper workflow json file here
