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

sample_name = "K4[Fe(CN)6]-polishing"
task_name = "CV_Const_ScanRate_smooth"
V_init = 0.0                    # Unit: Initial Voltage in V
V_max = 0.8                     # Unit: Highest Voltage in V
V_min = 0.0                     # Unit: Lowest Voltage in V
V_fin = 0.0                     # Unit: Final Voltage in V

scan_rate = 0.100               # Unit: Scan Rate in V/s
cycle_num: int = 50             # The Numer of Cycles as an Integer

enable_gui: bool = False        # GUI can be disabled for simple liquid transfer.

# ========== Sample Settings Above ========== #


def do_measurement(simulation: bool, logger: GraphicalInterface) -> None:

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=simulation)
    results = potentiostat.do_measurement(
        technique="CV",
        set_parameters={
            "IterationSettings": {
                "no_iterations": 1
            },
            "TechniqueParameters": {
                "Voltage Profile": {
                    "value": [V_init, V_max, V_min, V_init, V_fin]
                },
                "Scan Rate": {"value": [scan_rate] * 5},
                "Number of Cycles": {"value": cycle_num}
            }
        }
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

    simulation = False
    worker_thread = ThreadWithReturn(target=do_measurement, args=(simulation, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
