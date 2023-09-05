from etoad.Interface.GraphicalInterface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script demonstrate a simple DPV scan, without using the Workflow Manager.
    Without the usage of the GUI, the experiment can be run in the background.
"""

# ========== Sample Settings Below ========== #

SAMPLE_NAME = "K4[Fe(CN)6]_DPV_Single_Scan"
TASK_NAME = "Single Scan of DPV"
V_init = 0.8            # Unit: Initial Voltage in V
V_fin = 0               # Unit: Final Voltage in V
T_rest = 10             # The Resting Time Before the Scan

DISABLE_GUI: bool = False
SIMULATION: bool = False

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

    MakeObjects.mk_csv(results, logger=logger)  # Saves Raw Data as a CVS file.
    analyzer = MakeObjects.mk_analyzer(logger=logger)
    analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="DPV",
        analysis_settings={
            "Plot": {"title": "DPV of Single Scan"},
            "Peak Picking": {}
            # "Integration": {}
        },
        raw_data=results
    )
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(TASK_NAME, SAMPLE_NAME, DISABLE_GUI)
    gui_logger.info(f"Starting {TASK_NAME} of {SAMPLE_NAME}.")

    worker_thread = ThreadWithReturn(target=do_measurement, args=(SIMULATION, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
