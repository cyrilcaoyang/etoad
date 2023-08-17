from contextlib import contextmanager
from modbus_tk.modbus_rtu import RtuMaster
import modbus_tk.defines as cst
from serial import Serial
from logging import Logger
from ...Utils import log_exceptions


class AtmosphereHandler(object):
    """
    AtmosphereHandler Object that Controls a Relay via Modbus.
    Manages the Gas Atmosphere of the Connected Vessel(s) by Opening / Closing the Gas Supply.

    Public Methods to be Called from External:
        open_atmosphere() -> None: Context Manager for opening & closing the gas supply.
    """
    def __init__(self, logger: Logger, port: str, module_address: int, channel: int):
        """
        Instantiates the AtmosphereHandler object by setting the hardware connection ports.

        Args:
            logger: Logger object
            port: Name of the com port (e.g. "com3").
            module_address: Address of the module (set by pins on the device).
            channel: Channel to which the solenoid is connected.
        """
        self.logger: Logger = logger
        self._port: str = port
        self._module_address: int = module_address
        self._channel: int = channel

        self.logger.info(f"Inert Gas Handling initialized.")

    @contextmanager
    def open_atmosphere(self) -> None:
        """
        Public context manager for operations that should be performed under inert gas.
        Enters the CM by setting the valve to "open", and exits by setting it back to "close".
        """
        self._set_atmosphere(True)
        try:
            yield
        finally:
            self._set_atmosphere(False)

    @log_exceptions
    def _set_atmosphere(self, open_nitrogen: bool = False) -> None:
        """
        Sets the relay either to open (True) or closed (False)

        Args:
            open_nitrogen: Target status of the relay
        """
        with self._open_relay_connection():
            self.controller.execute(
                self._module_address,
                function_code=cst.WRITE_SINGLE_COIL,
                starting_address=self._channel,
                output_value=int(open_nitrogen)
            )
            if open_nitrogen:
                self.logger.debug(f"Nitrogen flow is ON!")
            else:
                self.logger.debug(f"Nitrogen flow is OFF!")

    @contextmanager
    def _open_relay_connection(self):
        """
        Context manager for opening and closing a serial port connection to the relay.
        Assures that the communication is only open for the actual operation (avoids communication failures).
        """
        ser: Serial = Serial(port=self._port, baudrate=9600, bytesize=8, parity="N", stopbits=1)
        self.controller: RtuMaster = RtuMaster(ser)
        self.controller.set_timeout(0.10)
        self.controller.set_verbose(True)
        try:
            yield
        finally:
            ser.close()
            del self.controller

