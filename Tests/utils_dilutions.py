from etoad.Utils import ThreadWithReturn
from test_utils.MakeObjects import mk_logger
from test_utils.LiquidTransfer import sample_to_cell

"""
    This python script demonstrate the Sampling System.
    A certain volume of sample solution will be diluted with electrolyte solution.
    You have the option to clean up the cell after this.
"""

# ========== Test Settings Below ========== #

sample_name = "K4[Fe(CN)6]"     # Name of the Chemical Solution
source_port = 9                 # The Port from which the Sample will be added.
sample_vol = 2.0                # The volume of sample in mL (< 5mL) to be diluted to 5 mL in the Cell.
total_vol = 10.0                # The total volume of the diluted solution

enable_gui: bool = True         # GUI can be disabled for simple liquid transfer.
clean_up: bool = False          # True = wash cell afterward with electrolyte solution.

# ========== Test Settings Above ========== #


if __name__ == "__main__":

    gui_logger = mk_logger(
        task_name="sampler_testing",
        sample_name=sample_name,
        enable_gui=enable_gui
    )
    worker_thread = ThreadWithReturn(
        target=sample_to_cell, args=(gui_logger, source_port, sample_vol, total_vol, clean_up)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
