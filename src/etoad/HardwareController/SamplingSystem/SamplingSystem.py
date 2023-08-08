import time
from pathlib import Path
from typing import Union
from logging import Logger

from matterlab_pumps import TecanXCPump
from .AtmosphereHandler import AtmosphereHandler
from ...Utils import ConfigLoader
from ...Utils import log_exceptions


class SamplingSystem:
    """
    Simple System for Sampling Liquids into a Measurement Cell using a Tecan Syringe Pump (Driver by Tony Wu).
    Current implementation only works for a system with a single multi-port syringe pump.

    Public Methods to be called from external:
        transfer_to_cell(source_port: int, volume: float) -> None
        dilute_cell(volume: float = 0, factor: float = 1) -> None
        purge_cell(purge_time: int = 10) -> None
        wash_cell(volume: float, cycles: int = 3) -> None
    """

    # TODO [at some point...]: Dead volume handling in the valve / syringe
    # For now, dead volume upon transferring small sample quantities can be dealt with by doing the sample transfer
    # first, and the dilution step later, so that all dead volume of sample is subsequently passed to the same
    # vessel as the sample. But that's not a generalizable solution...

    required_settings: set = {
        "com_port",
        "pump_volume",
        "pump_default_file",  # This is a weird af setting of the SerialDevice class that contradicts the idea of a default imo. But it's required atm – I've created an issue on the repo already.
        "cell_port",
        "wash_port",
        "waste_port",
        "relay_settings"
    }

    defined_ports: set = {
        "cell_port",
        "wash_port",
        "waste_port"
    }

    def __init__(
            self,
            config_file: Path,
            logger: Logger,
            pump_wash: int = 3,
            cell_filled: bool = True
    ):
        """
        Creates an instance of the SamplingSystem class.

        Args:
            config_file: Path to the configuration file. Needs to contain the specified keys in self.required_settings.
            logger: Logger object
            pump_wash: Number of initial washing steps. Default: 3
        """

        self._config: dict = ConfigLoader.load_config(config_file, self.required_settings)

        self.logger: Logger = logger

        self._atmosphere_handler: AtmosphereHandler = AtmosphereHandler(self.logger, **self._config["relay_settings"])

        self._pump: Union[TecanXCPump, None] = None
        self.cell_port: Union[int, None] = None

        self.wash_port: Union[int, None] = None
        self.waste_port: Union[int, None] = None

        self._set_ports()
        self._initialize_pump(pump_wash)

        if cell_filled:
            self.logger.debug(f"Measurement Cell was NOT empty.")
            self._cell_volume: float = 5.0
            self._empty_cell()
        else:
            self.logger.debug(f"Measurement Cell was empty.")
            self._cell_volume: float = 0

        self.logger.info("Sampling System Initialized. ")

    @log_exceptions
    def _initialize_pump(self, initial_wash: int = 3) -> None:
        """
        Creates an instance of the XCPump, sets the velocity and primes the pump.
        """
        self.logger.info(f"Pump initialization started.")
        self._pump: TecanXCPump = TecanXCPump(
            settings={
                "com_port": self._config["com_port"],
            },
            default_settings=self._config["pump_defaults_file"],
        )
        self._wash_pump(initial_wash)

    def _set_ports(self) -> None:
        """
        Sets the special ports "_cell_port", "wash_port" and "waste_port" as attributes of the class.
        """
        for port in self.defined_ports:
            setattr(self, port, self._config[port])
            self.logger.info(f"Pump {port} configured as {self._config[port]}.")

    @log_exceptions
    def transfer_to_cell(self, source_port: int, volume: float, wash_line: bool = False) -> None:
        """
        Transfers a given amount of liquid to the measurement cell.

        Args:
            source_port: Port from which the liquid should be moved to the cell.
            volume: Volume to be dispensed
            wash_line: Whether to wash the line to remove contaminations, e.g. from previous samples.
        """
        if wash_line:
            self._pump.draw_and_dispense(source_port, self.waste_port, self._config["dead_volume"], wait=1)
            self._wash_pump(1)
            self.logger.debug(f"Line from port {source_port} washed once.")

        self._pump.draw_and_dispense(source_port, self.cell_port, volume + self._config["dead_volume"], wait=2)
        self._update_cell_volume(volume)
        self.logger.debug(f"Dispensed {volume} mL from port {source_port} to cell.")

    @log_exceptions
    def dilute_cell(self, volume: float = 0, factor: float = 1) -> None:
        """
        Dilutes the solution in the cell based on either a fixed volume or a dilution factor.

        Args:
            volume: Volume of the wash solution (in mL) to be added. If given, the dilution factor is ignored.
            factor: Dilution factor.
        """
        if volume == 0:
            volume = self._cell_volume * (factor - 1)
            if factor > 1:
                self.logger.info(f"The Measurement Cell was diluted by a factor of {factor}.")

        self.transfer_to_cell(self.wash_port, volume)
        self.logger.debug(f"The cell was diluted by {volume} mL of wash solution.")

    @log_exceptions
    def purge_cell(self, purge_time: float = 10) -> None:
        """
        Purges the cell with inert gas.

        Args:
            purge_time: Purge time (in seconds).
        """
        self.logger.debug("N2 purging will be turned ON.")
        with self._atmosphere_handler.open_atmosphere():
            time.sleep(purge_time)

        self.logger.debug("N2 purging was turned OFF.")
        self.logger.info(f"Cell was purged with Nitrogen gas for {purge_time} sec.")

    @log_exceptions
    def _wash_pump(self, cycles=3):
        """
        Washes the syringe pump for three times with its volume of wash liquid.
        """
        for _ in range(cycles):
            self._pump.draw_and_dispense(self.wash_port, self.waste_port, self._config["pump_volume"], wait=1)

        self.logger.info(f"Pump washed {cycles} times.")

    @log_exceptions
    def wash_autosampler_position(self, sampler_position: int, no_cycles: int = 3) -> None:
        """
        Discards a sample in the autosampler and washes the vial.

        Args:
            sampler_position: Source port of the sample vial that should be cleaned.
            no_cycles: Number of wash cycles.
        """
        self._pump.draw_and_dispense(sampler_position, self.waste_port, 7.5, wait=1)
        self._wash_pump(1)
        for _ in range(no_cycles):
            self._pump.draw_and_dispense(self.wash_port, sampler_position, 5)
            self._pump.draw_and_dispense(sampler_position, self.waste_port, 6)
        self.logger.info(f"Sample position {sampler_position} was washed {no_cycles} times.")

    @log_exceptions
    def wash_cell(self, wash_volume: float, cycles=3) -> None:
        """
        Washes the cell for n times:
            - first time: 15 mL of wash solution to wash off also the sides of the measurement cell
            - other n-1 times: given volume of the wash solution.
        """
        self.logger.debug(f"Measurement Cell will be washed {cycles} times.")
        self._empty_cell()

        self.transfer_to_cell(self.wash_port, 15)
        time.sleep(5)
        self._empty_cell()

        for _ in range(cycles-1):
            self.transfer_to_cell(self.wash_port, wash_volume)
            time.sleep(5)
            self._empty_cell()

        self.logger.info(f"Measurement Cell was washed {cycles} times and emptied.")

    def _empty_cell(self):
        """
        Removes the entire amount of liquid from the cell.
        """
        self.logger.debug(f"Measurement Cell to be emptied.")

        with self._atmosphere_handler.open_atmosphere():
            self._pump.draw_and_dispense(self.cell_port, self.waste_port, self._cell_volume + 2, wait=1)
            self._update_cell_volume(-self._cell_volume)
            self.logger.debug(f"All liquid in Measurement Cell moved to waste.")

    def _update_cell_volume(self, volume: float) -> None:
        """
        Updates the cell volume based on the volume transferred to / from the cell.

        Args:
            volume: Volume added to (positive) / removed from (negative) the cell.
        """
        self._cell_volume += volume
        self.logger.debug(f"The amount of liquid in the Measurement Cell is {self._cell_volume} mL.")

    def disconnect(self) -> None:
        """
        Closes the connection to the pump by closing the pyvisa resource manager.
        """
        self._pump.manager.close()
        self.logger.info("Connection to the sampling system was successfully closed.")

