from etoad.Interface.GraphicalInterface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script demonstrate a simple SWV scan, without using the Workflow Manager.
    Without the usage of the GUI, the experiment can be run in the background.
"""

# ========== Sample Settings Below ========== #

SAMPLE_NAME = "K4[Fe(CN)6]_Pulse_Voltammetry"
TASK_NAME = "SWV_cyclic_scans_0.2mM_Ag-chip"

V_init = -0.4              # Unit: Initial Voltage in V
V_fin = 0.8                # Unit: Final Voltage in V
T_rest = 5                 # The Resting Time Before the Scan in seconds
CYCLE_NUM: int = 1         # The Numer of Cycles

DISABLE_GUI: bool = False      # This option can turn ON/OFF the GUI
SIMULATION: bool = False

# ========== Sample Settings Above ========== #


def do_measurement(simulation: bool, logger: GraphicalInterface):

    list_v_init = []
    list_v_fin = []

    for i in range(2*CYCLE_NUM):
        list_v_init.append(V_init) if i % 2 == 0 else list_v_init.append(V_fin)
        list_v_fin.append(V_fin) if i % 2 == 0 else list_v_fin.append(V_init)
    logger.info(f"The list of initial voltages is: {list_v_init}")
    logger.info(f"The list of final voltages is: {list_v_fin}")

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=simulation)
    results = potentiostat.do_measurement(
        technique="SWV",
        set_parameters={
            "IterationSettings": {"no_iterations": 2*CYCLE_NUM},
            "TechniqueParameters": {
                "Initial Voltage": {
                    "changed_over_iterations": True,
                    "value": list_v_init
                },
                "Rest Time": {
                    "value": T_rest
                },
                "Final Voltage": {
                    "changed_over_iterations": True,
                    "value": list_v_fin
                },
            }
        }
    )
    potentiostat.disconnect()

    _ = MakeObjects.mk_csv(results, logger=logger)

    analyzer = MakeObjects.mk_analyzer(logger=logger)
    analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="SWV",
        analysis_settings={
            "Plot": {"title": f"Cyclic SWV for {CYCLE_NUM} cycles"},
            "Peak Picking": {},
            "Integration": {}
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
