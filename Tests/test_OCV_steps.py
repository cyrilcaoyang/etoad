from etoad.Utils import ThreadWithReturn
from test_utils.MeasurePlot import measure_plot_ocv
import test_utils.MakeObjects as MakeObjects

"""
    This python script monitors Open Circuit Voltage (OCV) over time, in steps of time_per_step.
"""

# ========== Sample Settings Below ========== #

sample_name = "K4[Fe(CN)6]-OCV"   # Sample Name will the name of the folder that contains the data
task_name = "OCV_steps"

T_step = 15                       # Time per Step of Measurements in s, default: 15
voltage_interval = 0.1            # Unit: Voltage Interval in mV
time_interval = 0.05              # Unit: Time Interval Size in s
steps = 1                         # Unit: Number of Steps per cycle

channel_num: int = 1              # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True           # This option can turn ON/OFF the GUI
simulation: bool = False          # This option can turn ON/OFF the simulation mode

# ========== Sample Settings Above ========== #


if __name__ == "__main__":

    parameters = (T_step, voltage_interval, time_interval, steps)
    gui_logger = MakeObjects.mk_logger(task_name, sample_name, enable_gui)
    gui_logger.info(f"Starting {task_name} of {sample_name}.")

    simulation = False
    worker_thread = ThreadWithReturn(
        target=measure_plot_ocv,
        args=(gui_logger, parameters, channel_num, simulation)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
