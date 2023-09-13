from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script demonstrate the Sampling System.
    A certain volume of sample solution will be diluted with electrolyte solution.
    You have the option to clean up the cell after this.
"""

# ========== Test Settings Below ========== #

sample_name = "K4[Fe(CN)6]"     # Name of the Chemical Solution
source_port = 9                 # The Port from which the Sample will be added.
sample_vol = 1.0                # The volume of sample in mL (< 5mL) to be diluted to 5 mL in the Cell.
total_vol = 5.0                 # The total volume of the diluted solution

enable_gui: bool = True        # GUI can be disabled for simple liquid transfer.
clean_up: bool = False          # True = wash cell afterward with electrolyte solution.

# ========== Test Settings Above ========== #


def sampler_test(
        source_port: int,
        sample_vol: float,
        total_vol: float,
        clean_up: bool,
        logger: GraphicalInterface
) -> None:
    """
    This function performs the Sampling Demonstration.
    """
    sampler = MakeObjects.mk_sampler(logger=logger)

    # Transfers 0.5 mL from the sample position 9 to the cell
    sampler.transfer_to_cell(source_port=source_port, volume=sample_vol, wash_line=True)
    sampler.dilute_cell(volume=total_vol)
    sampler.purge_cell(10)

    if clean_up:
        sampler.wash_cell(wash_volume=total_vol, cycles=3)
        sampler.transfer_to_cell(source_port=12, volume=total_vol, wash_line=True)
    sampler.disconnect()
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(
        task_name="sampler_testing",
        sample_name=sample_name,
        enable_gui=enable_gui
    )
    worker_thread = ThreadWithReturn(
        target=sampler_test, args=(source_port, sample_vol, total_vol, clean_up, gui_logger)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
