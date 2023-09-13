from etoad.Interface.GraphicalInterface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script demonstrate a simple DPV scan, without using the Workflow Manager.
    Without the usage of the GUI, the experiment can be run in the background.
    The results are analyzed and plotted.
    
    The Data directory:
    is defined by .test_utils.PathFinder.py,
    which read settings read from .test_settings.data_settings.
"""

# ========== Sample Settings Below ========== #

sample_name = "K4[Fe(CN)6]_Pulse_Voltammetry"
task_name = "DPV_single_scan_0.2mM_Ag-chip"

V_init = 0.8            # Unit: Initial Voltage in V
V_fin = 0               # Unit: Final Voltage in V
T_rest = 10             # The Resting Time Before the Scan in seconds

enable_gui: bool = True        # This option can turn ON/OFF the GUI

# ========== Sample Settings Above ========== #


def do_measurement(simulation: bool, logger: GraphicalInterface):

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=simulation)
    results = potentiostat.do_measurement(
        technique="DPV",
        set_parameters={
            "IterationSettings": {"no_iterations": 1},
            "TechniqueParameters": {
                "Initial Voltage": {"value": V_init},
                "Rest Time": {"value": T_rest},
                "Final Voltage": {"value": V_fin},
            }
        }
    )
    potentiostat.disconnect()

    analyzer = MakeObjects.mk_analyzer(logger=logger)
    analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="DPV",
        analysis_settings={
            "Plot": {"title": "A Single Scan of DPV"},
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
