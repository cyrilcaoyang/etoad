from pathlib import Path
from Tests.test_utils.MakeObjects import mk_workflow_manager

"""
    This python script demonstrate workflows of multiple measurements of different techniques on different samples.
    Executes the workflow in the following steps using a GUI (which can be turned off):
        - Turns on the GUI
        - Sample transfer to the measurement cell
        - Runs iterations of Measurement-DataAnalysis-Visualization-Storage
        - Cell cleaning after the measurements
    
    Returns:
    a dictionary of results of all samples.
"""
# ========== Submit Samples Below ========== #

enable_gui = True                                # This option can turn ON/OFF the GUI
channel_num = 2                                  # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True

Job_Queue = (
    {"sample_name": "wash", "sample_location": 1, "workflow_path": Path("workflow_clean_vial.yaml")},
    # {"sample_name": "wash", "sample_location": 2, "workflow_path": Path("workflow_clean_vials.json")},
    # {"sample_name": "wash", "sample_location": 3, "workflow_path": Path("workflow_clean_vials.json")},
    # {"sample_name": "wash", "sample_location": 4, "workflow_path": Path("workflow_clean_vials.json")},
    # {"sample_name": "wash", "sample_location": 5, "workflow_path": Path("workflow_clean_vials.json")},
    # {"sample_name": "Fe-bpy", "sample_location": 6, "workflow_path": Path("workflow_stability_pos.json")},
    # {"sample_name": "Fe-bpy-44Me", "sample_location": 7, "workflow_path": Path("workflow_stability_pos.json")},
    # {"sample_name": "wash", "sample_location": 8, "workflow_path": Path("workflow_clean_vials.json")},
    # {"sample_name": "K4[Fe(CN)6]", "sample_location": 9, "workflow_path": Path("workflow_CV_peak_scan_rate.json")},
)

# ========== Submit Samples Above ========== #


def run_workflow(job_queue: tuple, channel_num: int, enable_gui: bool):
    manager = mk_workflow_manager(channel=channel_num, enable_gui=enable_gui)
    manager.submit_samples(job_queue)
    manager.start_system()


if __name__ == "__main__":
    run_workflow(Job_Queue, channel_num, enable_gui)
