import time
from etoad.Utils import ThreadWithReturn
from etoad.Interface.GraphicalInterface import GraphicalInterface
from test_utils.MakeObjects import mk_logger, mk_sampler

"""
    This python script demonstrate the Sampling System.
    A certain volume of sample solution will be diluted with electrolyte solution.
    You have the option to clean up the cell after this.
"""

# ========== Test Settings Below ========== #

sample_name = "sodium_anthraquinone_1_sulfonate_50mg_20mL_neutral"

source_port = 8     # The Port from which the Sample will be added.
sample_vol = 2.0        # The volume of sample in mL to be diluted to the Cell.
total_vol = 10.0     # The total volume of the diluted solution

enable_gui: bool = False         # GUI can be disabled for simple liquid transfer.
clean_up: bool = False          # True = wash cell afterward with electrolyte solution.
cell_filled: bool = True        # If the cell is filled, the solution will be drained first.

# ========== Test Settings Above ========== #


def drain_dilute_discard(
    logger: GraphicalInterface,
    sample_port: int,
    sample_vol: float,
    solvent_vol: float,
):
    # Instantiate the sampler and initiate it.
    sampler = mk_sampler(gui_logger, cell_filled)

    with sampler._atmosphere_handler.open_atmosphere():
        sampler.transfer_to_cell(sample_port, volume=sample_vol, wash_line=True)
        sampler.transfer_to_cell(source_port=12, volume=solvent_vol, wash_line=True)
        time.sleep(30)

    sampler.disconnect()
    logger.stop_gui()



if __name__ == "__main__":

    gui_logger = mk_logger(
        task_name="sampler_testing",
        sample_name=sample_name,
        enable_gui=enable_gui
    )

    worker_thread = ThreadWithReturn(
        target=drain_dilute_discard,
        args=(gui_logger, source_port, sample_vol, total_vol - sample_vol)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
