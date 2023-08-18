from pathlib import Path

from etoad.HardwareController import SamplingSystem
from etoad.Utils import timestamp_datetime
from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn

"""
    This python script demonstrate the Sampling System.
"""

# ========== Test Settings Below ========== #

Sample_Name = "K4[Fe(CN)6]"     # Name of the Chemical Solution
Source_Port = 9                 # The Port from which the Sample will be added.
Sample_Vol = 0.5                # The volume of sample in mL (< 5mL) to be diluted to 5 mL in the Cell.

Disable_GUI: bool = False        # GUI can be disabled for simple liquid transfer.
Clean_Up: bool = True
# ========== Test Settings Above ========== #


def define_paths() -> tuple:
    """
    This function defines the path of the working and data directory.
    """
    parent_dir = Path(__file__).parent
    with open(parent_dir / "test_settings" / "file_settings") as file:
        data_dir = Path(file.read())
    return parent_dir, data_dir


def make_logger(sample_name: str, disable_gui: bool) -> GraphicalInterface:
    """
    This function creates a logger for the experiment.
    """
    parent_dir, data_dir = define_paths()
    logger = GraphicalInterface(
        logging_config=parent_dir / "test_settings" / "logger_settings.json",
        log_file=data_dir / "Logs" / f"{timestamp_datetime()}_{sample_name}_transer_dilution.log",
        disable_gui=disable_gui
    )
    logger.sample_name = sample_name
    return logger


def sampler_test(
        source_port: int,
        sample_vol: float,
        clean_up: bool,
        logger: GraphicalInterface
) -> None:
    """
    This function performs the Sampling Demonstration.
    """
    parent_dir, data_dir = define_paths()
    sampler = SamplingSystem(
        config_file=parent_dir / "test_settings" / "sampler_settings.json",
        logger=logger,
        pump_wash=0,
        cell_filled=True
    )

    # Transfers 0.5 mL from the sample position 9 to the cell
    sampler.transfer_to_cell(
        source_port=source_port,
        volume=sample_vol,
        wash_line=True
    )
    sampler.dilute_cell(volume=5)

    if clean_up:
        sampler.wash_cell(
             wash_volume=5.0,
             cycles=3
        )
    sampler.disconnect()
    logger.stop_gui()


if __name__ == "__main__":
    gui_logger = make_logger(sample_name=Sample_Name, disable_gui=Disable_GUI)
    worker_thread = ThreadWithReturn(target=sampler_test, args=(Source_Port,Sample_Vol,Clean_Up,gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()


