from etoad.Interface.GraphicalInterface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script demonstrate a simple SWV scan, without using the Workflow Manager.
    Without the usage of the GUI, the experiment can be run in the background.
"""

# ========== Sample Settings Below ========== #

sample_name = "K4[Fe(CN)6]_Pulse_Voltammetry"       # This will the name of the folder that contains the data.
task_name = "SWV_cyclic_scans_0.2mM_Ag-chip"        # Specific test conditions.
disable_gui: bool = True                            # This option can turn ON/OFF the GUI.

V_init = -0.2                   # Unit: Initial Voltage in V
V_fin = 0.8                     # Unit: Final Voltage in V
T_rest = 5                      # The Resting Time Before the Scan in seconds
cycle_num: int = 20             # The Numer of Cycles

# ========== Sample Settings Above ========== #


def do_measurement(simulation: bool, logger: GraphicalInterface):

    list_v_init = []
    list_v_fin = []

    for i in range(2 * cycle_num):
        list_v_init.append(V_init) if i % 2 == 0 else list_v_init.append(V_fin)
        list_v_fin.append(V_fin) if i % 2 == 0 else list_v_fin.append(V_init)
    logger.info(f"The list of initial voltages is: {list_v_init}")
    logger.info(f"The list of final voltages is: {list_v_fin}")

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=simulation)
    results = potentiostat.do_measurement(
        technique="SWV",
        set_parameters={
            "IterationSettings": {"no_iterations": 2 * cycle_num},
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
            "Plot": {"title": f"Cyclic SWV for {cycle_num} cycles"},
            "Peak Picking": {},
            "Integration": {}
        },
        raw_data=results
    )
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(task_name, sample_name, disable_gui)
    gui_logger.info(f"Starting {task_name} of {sample_name}.")

    simulation = False
    worker_thread = ThreadWithReturn(target=do_measurement, args=(simulation, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
