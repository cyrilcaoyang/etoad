from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script demonstrate the Sampling System.
    A certain volume of sample solution will be diluted with electrolyte solution.
    You have the option to clean up the cell after this.
"""

# ========== Test Settings Below ========== #

SAMPLE_NAME = "K4[Fe(CN)6]"     # Name of the Chemical Solution
SOURCE_PORT = 9                 # The Port from which the Sample will be added.
SAMPLE_VOL = 0.5                # The volume of sample in mL (< 5mL) to be diluted to 5 mL in the Cell.
TOTAL_VOL = 5.0                 # The total volume of the diluted solution

DISABLE_GUI: bool = True        # GUI can be disabled for simple liquid transfer.
CLEAN_UP: bool = False          # True = wash cell afterward with electrolyte solution.

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
        sample_name=SAMPLE_NAME,
        disable_gui=DISABLE_GUI
    )
    worker_thread = ThreadWithReturn(
        target=sampler_test, args=(SOURCE_PORT, SAMPLE_VOL, TOTAL_VOL, CLEAN_UP, gui_logger)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
