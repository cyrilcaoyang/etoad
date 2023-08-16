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
    # {"sample_name": "K4[Fe(CN)6]", "sample_location": 9, "workflow_path": Path("workflow_stability_pos.json")},
    # {"sample_name": "Fe-ligand184-1", "sample_location": 1, "workflow_path": Path("")},
    # {"sample_name": "Fe-ligand184-2", "sample_location": 2, "workflow_path": Path("")},
    # {"sample_name": "CYR-181", "sample_location": 3, "workflow_path": Path("")},
    # {"sample_name": "wash", "sample_location": 4, "workflow_path": Path("")},
    # {"sample_name": "diquat-44Me-C2Br2", "sample_location": 5, "workflow_path": Path("workflow_stability_neg.json"),
    # {"sample_name": "wash", "sample_location": 6, "workflow_path": Path("")},
    # {"sample_name": "wash", "sample_location": 7, "workflow_path": Path("")},
    # {"sample_name": "wash", "sample_location": 8, "workflow_path": Path("workflow_clean_vials.json")},
    {"sample_name": "K4[Fe(CN)6]", "sample_location": 9, "workflow_path": Path("workflow_CV_peak_scan_rate.json")},
]

Disable_GUI: bool = False

# ========== Submit Samples Above ========== #


def run_workflow(job_queue=Job_Queue, disable_gui=Disable_GUI):

    parent_dir = Path(__file__).parent
    with open(parent_dir / "test_settings" / "file_settings") as file:
        data_dir = Path(file.read())

    manager: WorkflowManager = WorkflowManager(
        logger_settings=parent_dir / "test_settings" / "logger_settings.json",
        logfile=Path(data_dir / "Logs" / f"{timestamp_datetime()}_workflow_manager.log"),
        potentiostat_settings=parent_dir / "test_settings" / "potentiostat_settings.json",
        sampler_settings=parent_dir / "test_settings" / "sampler_settings.json",
        data_path=Path(data_dir / "DATA"),
        disable_gui=disable_gui,
    )

    manager.submit_samples(job_queue)
    manager.start_system()


if __name__ == "__main__":
    run_workflow()


# TODO: come up with a way to trigger a 'skip current run' exception, save data, and go to the next job
# test DPV-OCV-CV: after negative square wave, time.sleep for 30 sec and start CV from OCV
# change initial port to WASTE (This will be done with Han's new codes)
