import test_utils.MakeObjects as MakeObjects
from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn

"""
    This python script disconnet the potentiostat from the computer.
"""

# ========== Sample Settings Below ========== #

enable_gui: bool = True
simulation: bool = False    # This option can turn ON/OFF the Simulation Mode

# ========== Sample Settings Above ========== #


def do_measurement(simulation_mode: bool, logger: GraphicalInterface):
    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=simulation_mode)
    potentiostat.disconnect()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger('disconnection', 'None', enable_gui)
    gui_logger.info(f"Disconnecting the potentiostat.")

    worker_thread = ThreadWithReturn(target=do_measurement, args=(simulation, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
