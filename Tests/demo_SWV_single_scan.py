from etoad.Interface.GraphicalInterface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script demonstrate a simple SWV scan, without using the Workflow Manager.
    Without the usage of the GUI, the experiment can be run in the background.
"""

# ========== Sample Settings Below ========== #

TASK_NAME = "SWV_Single_Scan"
SAMPLE_NAME = "K4[Fe(CN)6]"
V_init = 1            # Unit: Initial Voltage in V
V_fin = -0.5               # Unit: Final Voltage in V
T_rest = 10             # The Resting Time Before the Scan

DISABLE_GUI: bool = False
SIMULATION: bool = False

# ========== Sample Settings Above ========== #


def do_measurement(simulation: bool,logger: GraphicalInterface, **kwargs):

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=simulation)
    results = potentiostat.do_measurement(
        technique="SWV",
        set_parameters={
            "IterationSettings": {"no_iterations": 1},
            "TechniqueParameters": {
                "Initial Voltage": {"value": V_init},
                "Rest Time": {"value": T_rest},
                "Final Voltage": {"value": V_fin},
            }
        }
    )

    MakeObjects.mk_csv(results, logger=logger)  # Saves Raw Data as CVS file
    potentiostat.disconnect()
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(TASK_NAME, SAMPLE_NAME, DISABLE_GUI)
    gui_logger.info(f"Starting {TASK_NAME} of {SAMPLE_NAME}.")

    worker_thread = ThreadWithReturn(target=do_measurement, args=(SIMULATION, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()

