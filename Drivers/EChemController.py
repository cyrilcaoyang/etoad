#!/usr/bin/env python
__author__ = 'Felix Strieth-Kalthoff'

from array import array
from pathlib import Path
from typing import Union, List
import numpy as np

from .Binaries import BINARY_PATH
import Drivers.BioLogic as KBIO  # TODO: Refactor and re-name to not import as global constant
from .DataStructures import *
from .Methods import *
from .DLL_Binding import EClibDLLInterface


class EChemController(object):
    """
    Minimalistic API-type Interface to the Bio-Logic Potentiostats.
    """
    def __init__(
            self,
            server: str,
            channel: int,

    ):
        """
        Instantiates a (absolutely minimalistic and preliminary) version of an API-type interface
        to the Bio-Logic Potentiostats.

        Args:
            server: String definition of the connection port of the instrument. # TODO: Rename?
            channel: Number of the channel to be used (counting from 1)


        Sets the following attributes:
            self.binary_path: Path to the directory where the binaries are located.
            self._dll_functions: Callable DLL interface to execute the DLL methods.
            self.device_id: ID of the connected potentiostat device.
            self.channel: Number of the channel (counting from 0)
            self.technique: Class describing the experimental technique (inherited from EChemMethod).
        """
        self.binary_path: Path = BINARY_PATH
        self._dll_functions: EClibDLLInterface = EClibDLLInterface(self.binary_path)

        self.channel: int = channel - 1
        self.device_id: int = self._connect(server)

        self.technique: Union[EChemMethod, None] = None

    def _connect(
            self,
            server: str,
            timeout: float = 5
    ) -> int:
        """
        Establishes the connection to the instrument.

        Parameters:
            server: String representation of the connection port of the instrument.
            timeout: Waiting time after which connection is cancelled.

        Returns:
            id: TBD
            device_name: TBD
        """
        # TODO: might be relevant to add some verbosity & checks here (device version, channel info)
        #  for metadata logging etc.
        device_id, device_info = c_int32(), KBIO.DeviceInfo()
        self._dll_functions("BL_Connect", server.encode(), timeout, device_id, device_info)

        return device_id.value

    #################################################################
    # METHODS RELATED TO LOADING TECHNIQUES AND DEFINING PARAMETERS #
    #################################################################

    def load_technique(
            self,
            technique: str,
            parameters: List[tuple]
    ) -> None:
        """
        Public Method.
        Sets the passed experimental technique to be used, loads and parses all experimental parameters.

        Args:
            technique: String definition of the measurement technique to be used. Must match the class name.
            parameters: List of tuples of method parameters: (Name, Type, Value, [Optional: Cycle])
        """
        self.technique = self._get_technique(technique)

        parameters_processed: KBIO.EccParams = self._load_parameters(parameters)

        self._dll_functions(
            "BL_LoadTechnique",
            self.device_id,
            self.channel,
            self.technique.method_file().encode(),
            parameters_processed,
            True,  # TODO: Figure out what is the role of the parameter "first"
            True,  # TODO: Figure out what is the role of the parameter "last"
            False  # TODO: Checks whether a Tkinter window pops up for parameter confirmation - optional / verbosity?
        )

    def _get_technique(
            self,
            technique: str,
    ) -> EChemMethod:
        """
        Method for evaluating the passed technique name to instantiate an EChemMethod object.

        Args:
            technique: Name of the measurement technique

        Returns:
            the specific measurement type object (EChemMethod class).
        """
        return eval(technique)(self.binary_path)

    def _load_parameters(
            self,
            parameters: List[tuple]
    ) -> KBIO.EccParams:
        """
        Processes the parameters passed as a list of tuples (Parameter_Name, Type, Value, [Optional: Index]).
        Converts all parameters into KBIO.EccParam objects.
        Generates and returns a single KBIO.EccParams object required for loading the method via the DLL.

        Args:
            parameters: List of all parameters, each given as a tuple.

        Returns:
            KBIO.EccParms object of all parameters.
        """
        parameter_objects = [self._define_parameter(*specification) for specification in parameters]

        no_params = len(parameter_objects)
        parameter_array = KBIO.ECC_PARM_ARRAY(no_params)

        for i, param_obj in enumerate(parameter_objects):
            parameter_array[i] = param_obj

        return KBIO.EccParams(no_params, parameter_array)

    def _define_parameter(
            self,
            label: str,
            parameter_type: type,
            value: Union[int, float, bool],
            index: int = 0,
    ) -> KBIO.EccParam:
        """
        Calls the respective internal function to write the parameter definition to the return object.

        Args:
            label: String of the variable name, as given in the DLL documentation.
            parameter_type: Python type of the variable
            value: Value of the variable
            index: Index of the variable (in case this variable is set multiple times, 0 otherwise).

        Returns:
            None
        """
        type_definitions: dict = {
            int: "BL_DefineIntParameter",
            float: "BL_DefineSglParameter",
            bool: "BL_DefineBoolParameter"
        }
        # TODO: Move this dictionary and a corresponding call method to the DLLInterface!

        parameter = KBIO.EccParam()

        function_name = type_definitions[parameter_type]
        self._dll_functions(function_name, label.encode(), value, index, parameter)

        return parameter

    ########################################################
    # METHODS RELATED TO ACTUALLY PERFORMING A MEASUREMENT #
    ########################################################

    def do_measurement(
            self
    ) -> np.ndarray:
        """
        Performs the actual measurement by loading the technique and starting measurements on the channel.

        Returns:
            results: 2D Numpy array of the results data
        """
        # TODO: include verbosity here
        # TODO: Refactor and modularize
        if not self.technique:
            raise ModuleNotFoundError("No Method has been loaded.")

        results: np.ndarray = np.array([])

        self._dll_functions("BL_StartChannel", self.device_id, self.channel)  # TODO: handle via context manager?

        while True:
            data: tuple = self._get_data()
            data_decoded, metadata = self.technique.decode_data(data, self._decode_numeric_to_single)

            # TODO: Refactor into smaller methods, maybe via exception handling in the decoding function?
            if results.size == 0:
                results = data_decoded
            elif data_decoded.size == 0:
                if metadata["status"] == "STOP":
                    self.stop_channel()
                    # TODO: Does this allow for re-running the same measurement on a different sample?
                    #  If not, the technique should be unloaded here -> _close_measurement method?
                    break
            else:
                results = np.append(results, data_decoded, axis=0)

        return results

    def _get_data(
            self
    ) -> tuple:
        """
        Reads the data from the current channel, returns the metadata, current values, and all read-in data.

        Returns:
            current_values: CurrentValues object as a data infrastructure (save instrument state from DLL methods).
            data_info: DataInfo object as a data infrastructure to save method metadata from the DLL methods.
            data_buffer: Array of all read data.
        """
        data_buffer: KBIO.DataBuffer = KBIO.DataBuffer()
        data_info: KBIO.DataInfo = KBIO.DataInfo()
        current_values: KBIO.CurrentValues = KBIO.CurrentValues()

        self._dll_functions("BL_GetData", self.device_id, self.channel, data_buffer, data_info, current_values)

        rows: int = data_info.NbRows
        columns: int = data_info.NbCols
        data_buffer = array('L', data_buffer[:rows*columns])

        return current_values, data_info, data_buffer

    def stop_channel(
            self
    ) -> None:
        """
        Method to shut down a channel after completion of a measurement.
        """
        self._dll_functions("BL_StopChannel", self.device_id, self.channel)

    def _decode_numeric_to_single(
            self,
            raw_numeric: Union[str, int, float]
    ) -> float:
        """
        Method that uses the DLL to convert a raw numeric value into a single Python float.

        Returns:
            raw_numeric: Raw numerical value
        """
        result = c_float()
        self._dll_functions("BL_ConvertNumericIntoSingle", raw_numeric, result)
        return result.value
