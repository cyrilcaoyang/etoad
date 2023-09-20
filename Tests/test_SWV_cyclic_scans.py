from etoad.Interface.GraphicalInterface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script demonstrate a simple SWV scan, without using the Workflow Manager.
    Without the usage of the GUI, the experiment can be run in the background.
"""

# ========== Sample Settings Below ========== #

sample_name = "K4[Fe(CN)6]_Pulse_Voltammetry"                   # The name of the folder that contains the data.
task_name = "SWV_multiple_scan_smooth-GC_Pt_SHE"                # Specific test conditions.

V_init = 0.0                                                    # Initial Voltage in V
V_fin = 1.2                                                     # Final Voltage in V
T_rest = 5                                                      # The Resting Time Before the Scan in seconds
cycle_num: int = 5                                              # The Numer of Cycles

channel_num: int = 2                                            # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True                                         # This option can turn ON/OFF the GUI
simulation: bool = False                                        # This option can turn ON/OFF the simulation mode

# ========== Pulse Settings Below ========== #

Pulse_h = 0.025                                                 # Pulse Height in V, default: 0.025
Pulse_w = 0.200                                                 # Pulse Width in seconds, default: 0.200
Step_h = 0.010                                                  # Step Height in V, default: 0.010
average_percent = 0.800                                         # Averaging Percent Interval (0,1), default: 0.800

# ========== Pulse Settings Above ========== #


def do_measurement(
    logger: GraphicalInterface,
    para_range_time: list,
    pulse_para: list,
    channel: int,
    simulation_opt: bool
) -> None:

    list_v_init = []
    list_v_fin = []

    for i in range(2 * cycle_num):
        list_v_init.append(para_range_time[0]) if i % 2 == 0 else list_v_init.append(para_range_time[1])
        list_v_fin.append(para_range_time[1]) if i % 2 == 0 else list_v_fin.append(para_range_time[0])
    logger.info(f"The list of initial voltages is: {list_v_init}")
    logger.info(f"The list of final voltages is: {list_v_fin}")

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, channel=channel, sim=simulation_opt)
    results = potentiostat.do_measurement(
        technique="SWV",
        set_parameters={
            "IterationSettings": {"no_iterations": 2 * cycle_num},
            "TechniqueParameters": {
                "Initial Voltage": {
                    "changed_over_iterations": True,
                    "value": list_v_init
                },
                "Rest Time": {"value": T_rest},
                "Final Voltage": {
                    "changed_over_iterations": True,
                    "value": list_v_fin
                },
                "Pulse Height": {"value": pulse_para[0]},
                "Pulse Width": {"value": pulse_para[1]},
                "Step Height": {"value": pulse_para[2]},
                "Start Averaging Interval": {"value": pulse_para[3]}
            }
        },
        channel=channel
    )
    potentiostat.disconnect()

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

    gui_logger = MakeObjects.mk_logger(task_name, sample_name, enable_gui)
    gui_logger.info(f"Starting {task_name} of {sample_name}.")

    range_time = [V_init, V_fin, T_rest]                      # The range of voltages and resting time
    P_para = [Pulse_h, Pulse_w, Step_h, average_percent]      # The parameters of the pulse

    worker_thread = ThreadWithReturn(
        target=do_measurement,
        args=(gui_logger, range_time, P_para, channel_num, simulation)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
