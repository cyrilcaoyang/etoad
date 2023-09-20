import test_utils.MakeObjects as MakeObjects
from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn

"""
    This python script disconnects the potentiostat from the computer.
        For example, if a measurement is interrupted, the potentiostat may still be connected to the computer.
        Now, it would be dangerous to take out the one of the electrodes, i.e. the working electrode for polishing.
"""

# ========== Sample Settings Below ========== #

enable_gui: bool = False
channel_num: int = 2            # The channel number of the potentiostat, either 1 or 2.

# ========== Sample Settings Above ========== #


def do_measurement(simulation_mode: bool, logger: GraphicalInterface):
    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=simulation_mode)
    potentiostat.disconnect()
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger('disconnection', 'None', enable_gui)
    gui_logger.info(f"Disconnecting the potentiostat.")

    worker_thread = ThreadWithReturn(target=do_measurement, args=(False, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
