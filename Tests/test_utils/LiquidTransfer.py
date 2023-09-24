from etoad.Interface import GraphicalInterface
from .MakeObjects import mk_sampler
from logging import Logger


def sample_to_cell(
    logger: GraphicalInterface,
    source_port: int,
    sample_vol: float,
    total_vol: float,
    clean_up: bool,
) -> None:
    """
    This function performs the Sample transfer and dilution in the Cell.
    """
    sampler = mk_sampler(logger=logger)

    # Transfers 0.5 mL from the sample position 9 to the cell
    sampler.transfer_to_cell(source_port=source_port, volume=sample_vol, wash_line=True)
    sampler.dilute_cell(volume=total_vol)
    sampler.purge_cell(10)

    if clean_up:
        sampler.wash_cell(wash_volume=total_vol, cycles=3)
        sampler.transfer_to_cell(source_port=12, volume=total_vol, wash_line=True)
    sampler.disconnect()
    logger.stop_gui()


def wash_cell_refill(
    logger: Logger,
    repeat: int,
    refill_volume: float,
) -> None:

    sampler = mk_sampler(logger=logger)
    sampler.wash_cell(repeat)
    if refill_volume == 0:
        logger.debug("No refill volume is given. Cell is empty.")
    else:
        sampler.transfer_to_cell(source_port=12, volume=refill_volume, wash_line=True)

