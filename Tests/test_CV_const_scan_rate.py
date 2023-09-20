from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script demonstrate the CV scans with constant scan rates, without using the Workflow Manager
    Without the usage of the GUI, the experiment can be run in the background.
    The results are analyzed and plotted.
    
    The Data directory:
    is defined by .test_utils.PathFinder.py,
    which read settings read from .test_settings.data_settings.
"""

# ========== Sample Settings Below ========== #

sample_name = "Fe(II)-4COOH4Me_CV-Const-ScanRate"                  # The name of the folder that contains the data.
task_name = "CV_Const_ScanRate_smooth-GC_Pt_SHE"               # Specific test conditions.

V_init = 0.4                                                   # Initial Voltage in V
V_max = 1.2                                                    # Highest Voltage in V
V_min = 0.4                                                    # Lowest Voltage in V
V_fin = 0.4                                                    # Final Voltage in V

scan_rate = 0.500                                              # Scan Rate in V/s
cycle_num: int = 5                                           # The Numer of Cycles as an Integer, > 1

channel_num: int = 1                                           # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True                                        # GUI can be disabled for simple liquid transfer.
simulation: bool = False                                       # Simulation mode can be enabled for testing.

# ========== Sample Settings Above ========== #


def do_measurement(logger: GraphicalInterface, v_range: list, channel: int, simulation_opt: bool) -> None:

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, channel=channel, sim=simulation_opt)
    results = potentiostat.do_measurement(
        technique="CV",
        set_parameters={
            "IterationSettings": {"no_iterations": 1},
            "TechniqueParameters": {
                "Voltage Profile": {"value": v_range},
                "Scan Rate": {"value": [scan_rate] * 5},
                "Number of Cycles": {"value": cycle_num}
            }
        },
        channel=channel
    )
    potentiostat.disconnect()

    analyzer = MakeObjects.mk_analyzer(logger=logger)
    analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="CV",
        analysis_settings={
            "Plot": {"title": "Cyclic Voltammetry of a Single Scan"},
            "Peak Picking": {},
            "Integration": {}
        },
        raw_data=results
    )
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(task_name, sample_name, enable_gui)
    gui_logger.info(f"Starting {task_name} of {sample_name}.")

    V_range = [V_init, V_max, V_min, V_init, V_fin]
    worker_thread = ThreadWithReturn(
        target=do_measurement,
        args=(gui_logger, V_range, channel_num, simulation)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
