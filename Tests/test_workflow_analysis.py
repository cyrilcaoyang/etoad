import test_utils.MakeObjects as MakeObjects
from pathlib import Path

"""

    This python script demonstrate workflows of multiple measurements of different techniques on different samples.

    Executes the workflow in the following steps using a GUI (which can be turned off):
        - Turns on the GUI
        - Sample transfer to the measurement cell
        - First measurement (Square Wave Voltammetry)
        - Data analysis, visualization and storage
        - Second measurement (Cyclic Voltammetry measurement) based on parameters inferred from the first one.
        - Data analysis, visualization and storage
        - ...Potentially more measurements...
        - Cell cleaning after the measurements
    
    Returns:
    a dictionary of results of all samples.
    
    # TODO: come up with a way to trigger a 'skip current run' exception, save data, and go to the next job
    
"""
# ========== Submit Samples Below ========== #
#   Example:
#   {"sample_name": "K4[Fe(CN)6]", "sample_location": 9, "workflow_path": Path("test_stability_pos.json")}

GUI: bool = True
Job_Queue: tuple = (
    # {"sample_name": "wash", "sample_location": 1, "workflow_path": Path("workflow_clean_vials.json")},
    # {"sample_name": "wash", "sample_location": 2, "workflow_path": Path("workflow_clean_vials.json")},
    # {"sample_name": "wash", "sample_location": 3, "workflow_path": Path("workflow_clean_vials.json")},
    # {"sample_name": "wash", "sample_location": 4, "workflow_path": Path("workflow_clean_vials.json")},
    # {"sample_name": "wash", "sample_location": 5, "workflow_path": Path("workflow_clean_vials.json")},
    # {"sample_name": "Fe-bpy", "sample_location": 6, "workflow_path": Path("workflow_stability_pos.json")},
    # {"sample_name": "wash", "sample_location": 7, "workflow_path": Path("workflow_clean_vials.json")},
    # {"sample_name": "wash", "sample_location": 8, "workflow_path": Path("workflow_clean_vials.json")},
    {"sample_name": "K4[Fe(CN)6]", "sample_location": 9, "workflow_path": Path("workflow_stability_pos.json")},
)

# ========== Submit Samples Above ========== #


def run_workflow(job_queue=Job_Queue, enable_gui=GUI):

    manager = MakeObjects.mk_workflow_manager(enable_gui=enable_gui)
    manager.submit_samples(job_queue)
    manager.start_system()


if __name__ == "__main__":
    run_workflow()
