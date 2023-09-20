from pathlib import Path
from test_utils.MakeObjects import mk_workflow_manager

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

enable_gui = True                                # This option can turn ON/OFF the GUI
channel_num = 1                                  # The channel number of the potentiostat, either 1 or 2.
job_queue: tuple = (
    # {"sample_name": "wash", "sample_location": 1, "workflow_path": Path("workflow_clean_vials.json")},
    {"sample_name": "K4[Fe(CN)6]", "sample_location": 9, "workflow_path": Path("workflow_clean_vials.yaml")},
)

# ========== Submit Samples Above ========== #


def run_workflow(queue: tuple, channel: int, gui: bool):
    manager = mk_workflow_manager(channel=channel,enable_gui=gui)
    manager.submit_samples(queue)
    manager.start_system()


if __name__ == "__main__":
    run_workflow(queue=job_queue, channel=channel_num, gui=enable_gui)
