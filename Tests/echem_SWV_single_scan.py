from typing import Any
from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn, Timestamps

import Tests.utils_makeobjects as MakeObjects
from Tests.utils_unitoperations import do_experiment, do_analysis

"""
    This python script demonstrate a simple SWV scan, with sample already in the Cell.
    The results are analyzed and plotted, and saved in the sample folder.
"""

# ========== Sample Settings Below ========== #

sample_name = f"2,6-AQDS_{Timestamps.timestamp_date()}-base"
task_name = "SWV_single_scan_smooth-GC_Pt_SHE"

V_init = 1.2                                                    # Initial Voltage in V
V_fin = -1.0                                                    # Final Voltage in V
T_rest = 10                                                     # The Resting Time Before the Scan in seconds

channel_num: int = 2                                           # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True                                         # This option can turn ON/OFF the GUI
simulation: bool = False                                        # This option can turn ON/OFF the simulation mode

Pulse_h = 0.025                                                 # Pulse Height in V, default: 0.025
Pulse_w = 0.200                                                 # Pulse Width in seconds, default: 0.200
Step_h = 0.010                                                  # Step Height in V, default: 0.010
average_percent = 0.800                                         # Averaging Percent Interval (0,1), default: 0.800

swv_test_settings: dict = {
    "IterationSettings": {"no_iterations": 1},
    "TechniqueParameters": {
        "Initial Voltage": {"value": V_init},
        "Final Voltage": {"value": V_fin},
        "Rest Time": {"value": T_rest},
        "Pulse Height": {"value": Pulse_h},
        "Pulse Width": {"value": Pulse_w},
        "Step Height": {"value": Step_h},
        "Start Averaging Interval": {"value": average_percent},
        "End Averaging Interval": {"value": 1.0}
    }
}

swv_analysis_settings: dict = {
    "Plot": {"title": "A Single Scan of SWV"},
    "Peak Picking": {}
}

# ========== Sample Settings Above ========== #


def do_experiment_analysis(
        logger: GraphicalInterface,
        technique: str,
        channel: int,
        measurement_settings: dict,
        analysis_settings: dict,
) -> Any:

    exp_results = do_experiment(logger, technique, channel, measurement_settings)
    analysis_results = do_analysis(logger, technique, analysis_settings, exp_results)
    logger.stop_gui()
    return analysis_results


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(task_name, sample_name, enable_gui)
    gui_logger.info(f"Starting {task_name} of {sample_name}.")

    worker_thread = ThreadWithReturn(
        target=do_experiment_analysis,
        args=(gui_logger, "SWV", channel_num, swv_test_settings, swv_analysis_settings)
    )
    worker_thread.start()
    gui_logger.start_gui()
    result = worker_thread.join()

