from etoad.Interface.GraphicalInterface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script demonstrate a simple DPV scan, without using the Workflow Manager.
    Without the usage of the GUI, the experiment can be run in the background.
    The results are analyzed and plotted.
"""

# ========== Sample Settings Below ========== #

sample_name = "K4[Fe(CN)6]_Pulse_Voltammetry"
task_name = "DPV_single_scan_smooth-GC_Pt_SHE"

V_init = -0.5                                                   # Unit: Initial Voltage in V
V_fin = 1.2                                                     # Unit: Final Voltage in V
T_rest = 10                                                     # The Resting Time Before the Scan in seconds

Pulse_h = 0.010                                                 # Pulse Height in V, default: 0.010
Pulse_w = 0.100                                                 # Pulse Width in seconds, default: 0.100
Step_h = 0.005                                                  # Step Height in V, default: 0.005
Step_w = 0.500                                                  # Step Width in seconds, default: 0.500
start_percent = 0.800                                           # Start Averaging Interval (0,1), default: 0.800
end_percent = 1.000                                             # End Averaging Interval (0,1), default: 1.000

channel_num: int = 1                                            # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True                                         # This option can turn ON/OFF the GUI
simulation: bool = False                                        # This option can turn ON/OFF the simulation mode

# ========== Sample Settings Above ========== #


def do_measurement(
        logger: GraphicalInterface,
        para_range_time: list,
        pulse_para: list,
        channel: int,
        simulation_opt: bool
) -> None:

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, channel=channel, sim=simulation_opt)
    results = potentiostat.do_measurement(
        technique="DPV",
        set_parameters={
            "IterationSettings": {"no_iterations": 1},
            "TechniqueParameters": {
                "Initial Voltage": {"value": para_range_time[0]},
                "Final Voltage": {"value": para_range_time[1]},
                "Rest Time": {"value": para_range_time[2]},
                "Pulse Height": {"value": pulse_para[0]},
                "Pulse Width": {"value": pulse_para[1]},
                "Step Height": {"value": pulse_para[2]},
                "Step Width": {"value": pulse_para[3]},
                "Start Averaging Interval": {"value": pulse_para[4]},
                "End Averaging Interval": {"value": pulse_para[5]}
            }
        },
        channel=channel
    )
    potentiostat.disconnect()

    analyzer = MakeObjects.mk_analyzer(logger=logger)
    analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="DPV",
        analysis_settings={
            "Plot": {"title": "A Single Scan of SWV"},
            "Peak Picking": {}
        },
        raw_data=results
    )
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(task_name, sample_name, enable_gui)
    gui_logger.info(f"Starting {task_name} of {sample_name}.")

    range_time = [V_init, V_fin, T_rest]                                       # The range of voltages and resting time
    P_para = [Pulse_h, Pulse_w, Step_h, Step_w, start_percent, end_percent]    # The pulse parameters
    worker_thread = ThreadWithReturn(
        target=do_measurement,
        args=(gui_logger, range_time, P_para, channel_num, simulation)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
