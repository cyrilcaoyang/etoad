import threading
from ftdi_serial import Serial


class Hotplate(object):
    """
    IKA RCT 5 digital Hotplate, by Yang Cao
    Modified and Trimmed from code by Veronica Lai @ Jason Hein group
    """

    # hex command characters for data transmission
    SP_HEX = "\x20"  # space or blank
    CR_HEX = "\x0d"  # carriage return
    LF_HEX = "\x0a"  # line feed or new line
    DOT_HEX = "\x2E"  # dot
    LINE_ENDING = CR_HEX + LF_HEX  # each individual command and each response are terminated CR LF
    LINE_ENDING_ENCODED = LINE_ENDING.encode()

    # default connection parameters
    CONNECTION_SETTINGS = dict(
        baudrate=9600,
        data_bits=Serial.DATA_BITS_7,
        stop_bits=Serial.STOP_BITS_1,
        parity=Serial.PARITY_EVEN,
    )

    # constant names are the functions, and the values are the corresponding NAMUR commands
    READ_THE_DEVICE_NAME = "IN_NAME"
    START_THE_HEATER = "START_1"
    STOP_THE_HEATER = "STOP_1"
    START_THE_MOTOR = "START_4"
    STOP_THE_MOTOR = "STOP_4"
    ADJUST_THE_SET_TEMPERATURE_VALUE = "OUT_SP_1"
    SET_TEMPERATURE_VALUE = "OUT_SP_1 "  # requires a value to be appended to the end of the command
    READ_ACTUAL_EXTERNAL_SENSOR_VALUE = "IN_PV_1"
    READ_ACTUAL_HOTPLATE_SENSOR_VALUE = "IN_PV_2"
    READ_RATED_TEMPERATURE_VALUE = "IN_SP_1"
    READ_STIRRING_SPEED_VALUE = "IN_PV_4"
    READ_RATED_SPEED_VALUE = "IN_SP_4"
    ADJUST_THE_SET_SPEED_VALUE = "OUT_SP_4"
    SET_SPEED_VALUE = "OUT_SP_4 "  # requires a value to be appended to the end of the command

    def __init__(self, device_port: str, **kwargs):
        """
        device_port: port on computer to connect to the hotplate. For example, 'COM3'
        """
        self.ser: Serial = None
        self._lock = threading.Lock()
        self._device_port = device_port
        self.connect()

    @property
    def target_stir_rate(self) -> float:
        """
        Stir rate hotplate is set to go to
        """
        return self.read_rated_speed_value()

    @target_stir_rate.setter
    def target_stir_rate(self, value):
        self.set_speed_value(value=value)

    def set_target_stir_rate(self, value):
        self.target_stir_rate = value

    @property
    def probe_temperature(self):
        """
        The temperature (degrees C) picked up by the temperature probe
        """
        return self.read_actual_external_sensor_value()

    @property
    def target_temperature(self) -> float:
        """
        Temperature hotplate is set to go to
        """
        return self.read_rated_temperature_value()

    @target_temperature.setter
    def target_temperature(self, value, ):
        self.set_temperature_value(value=value)

    def set_target_temperature(self, value):
        self.target_temperature = value

    @property
    def hotplate_sensor_temperature(self) -> float:
        """
        The value (degrees C) that the hotplate itself is at
        """
        return self.read_actual_hotplate_sensor_value()

    def connect(self):
        try:
            if self.ser is None:
                cn = Serial(device_port=self._device_port,
                            **self.CONNECTION_SETTINGS,
                            )
                self.ser = cn
            else:
                self.ser.connect()
        except Exception:
            raise print('Could not connect to the plate, make sure the right port was selected')

    def disconnect(self):
        """
        Stop heating and stirring and close the serial port
        """
        if self.ser is not None:
            try:
                if self.ser.connected:
                    self.stop_heating()
                    self.stop_stirring()
                    self.ser.disconnect()
            except Exception:
                raise print('Could not disconnect from plate')

    def _send_and_receive(self, command: str):
        """
        Send a command, get a response back, and return the response
        :param str, command: a command that will give back a response - these will be:
            READ_THE_DEVICE_NAME
            READ_ACTUAL_EXTERNAL_SENSOR_VALUE
            READ_ACTUAL_HOTPLATE_SENSOR_VALUE
            READ_STIRRING_SPEED_VALUE
            READ_RATED_TEMPERATURE_VALUE
            READ_RATE_SET_SAFETY_TEMPERATURE_VALUE
            READ_RATE_SPEED_VALUE
        """
        with self._lock:
            # format the command to send so that it terminates with the line ending (CR LF)
            formatted_command: str = command + self.LINE_ENDING
            formatted_command_encoded = formatted_command.encode()
            # this is the response, and is returned
            return_string = self.ser.request(data=formatted_command_encoded,
                                             line_ending=self.LINE_ENDING_ENCODED,
                                             ).decode()
            # all the functions that would use this function, except when asking for the device name, returns a number.
            # however the return string type for all the other functions is a string of the type '#.# #', so we want to
            # change that into a float instead so it can be easily used
            if return_string == 'RCT digital':
                return 'RCT digital'
            else:
                formatted_return_float = float(
                    return_string.split()[0])  # return just the information we want as a float
            return formatted_return_float

    def _send(self, command: str):
        """
        Send a command
        :param str, command: a command with optional parameter's included if required (such as for setting temperature
            or stirring rate
        :return:
        """
        with self._lock:
            # format the command to send so that it terminates with the line ending (CR LF)
            formatted_command: str = command + self.LINE_ENDING
            formatted_command_encoded = formatted_command.encode()
            self.ser.write(data=formatted_command_encoded)  # commands need to be encoded when sent

    def read_device_name(self):
        return self._send_and_receive(command=self.READ_THE_DEVICE_NAME)

    def read_actual_external_sensor_value(self):
        """
        read and return the temperature (degrees C) picked up by the temperature probe
        """
        return self._send_and_receive(command=self.READ_ACTUAL_EXTERNAL_SENSOR_VALUE)

    def read_actual_hotplate_sensor_value(self):
        return self._send_and_receive(command=self.READ_ACTUAL_HOTPLATE_SENSOR_VALUE)

    def read_stirring_speed_value(self):
        return self._send_and_receive(command=self.READ_STIRRING_SPEED_VALUE)

    def read_rated_temperature_value(self):
        """
        read and return the temperature (degrees C) that the hotplate was set to maintain
        """
        return self._send_and_receive(command=self.READ_RATED_TEMPERATURE_VALUE)

    def read_rated_speed_value(self):
        return self._send_and_receive(command=self.READ_RATED_SPEED_VALUE)

    def adjust_the_set_temperature_value(self):
        self._send(command=self.ADJUST_THE_SET_TEMPERATURE_VALUE)

    def set_temperature_value(self, value):
        command = self.SET_TEMPERATURE_VALUE + str(value) + ' '
        self._send(command=command)

    def adjust_the_set_speed_value(self):
        self._send(command=self.ADJUST_THE_SET_SPEED_VALUE)

    def set_speed_value(self, value):
        command = self.SET_SPEED_VALUE + str(value) + ' '
        self._send(command=command)

    def start_heating(self):
        self._send(command=self.START_THE_HEATER)

    def stop_heating(self):
        self._send(command=self.STOP_THE_HEATER)

    def start_stirring(self):
        self._send(command=self.START_THE_MOTOR)

    def stop_stirring(self):
        self._send(command=self.STOP_THE_MOTOR)


class MockMagneticStirrer(Hotplate):
    """
    A mock class of the magnetic stirrer class to test things out without having to connect to one. All commands
    will now instead log
    """

    def __init__(self, device_port='COM42', **kwargs):

        # for returning dummy values
        self._temperature = 25.0  # probe temperature
        self._stir_rate = 0
        self._target_temperature = 25.0
        self._safety_temperature = 150.0
        self._target_stir_rate = 100
        self._hot_plate_sensor_value = self._temperature * 1.1
        self._wd_time = 100.0

        Hotplate.__init__(self, device_port=device_port, **kwargs)

        self.heating: bool = False  # true if hot plate is heating
        self.stirring: bool = False  # true if hot plate is heating

    def connect(self):
        return

    def _send(self, command: str, ):
        # todo update send to update dummy values, remove the specific methds below
        if command in [self.START_THE_HEATER, self.STOP_THE_HEATER, self.START_THE_MOTOR, self.STOP_THE_MOTOR]:
            return
        elif command[:9] == self.SET_TEMPERATURE_VALUE:
            temperature_to_set_to = command[9:-1]
            if temperature_to_set_to == '':
                return
            else:
                self._target_temperature = float(temperature_to_set_to)
                self._temperature = float(temperature_to_set_to)
        elif command[:9] == self.SET_SPEED_VALUE:
            stir_rate_to_set_to = command[9:-1]
            if stir_rate_to_set_to == '':
                return
            else:
                self._target_stir_rate = stir_rate_to_set_to
                self._stir_rate = stir_rate_to_set_to

    def _send_and_receive(self,
                          command: str,
                          ):
        if command == self.READ_THE_DEVICE_NAME:
            return 'C-MAG HS7'
        elif command == self.READ_ACTUAL_EXTERNAL_SENSOR_VALUE:
            return float(self._temperature)
        elif command == self.READ_ACTUAL_HOTPLATE_SENSOR_VALUE:
            return float(self._hot_plate_sensor_value)
        elif command == self.READ_STIRRING_SPEED_VALUE:
            return float(self._stir_rate)
        elif command == self.READ_RATED_TEMPERATURE_VALUE:
            return float(self._target_temperature)
        elif command == self.READ_RATED_SPEED_VALUE:
            return float(self._target_stir_rate)
