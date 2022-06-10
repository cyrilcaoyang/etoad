#!/usr/bin/env python
__author__ = 'Felix Strieth-Kalthoff'

import ctypes
from pathlib import Path
from typing import Any

from .Utils import get_bit_mode
from .DataStructures import *
import Potentiostat.BioLogic as KBIO


class EClibDLLInterface(object):

    dll_files: dict = {
        32: "EClib.dll",
        64: "EClib64.dll"
    }

    eclib_functions: dict = {
        "BL_GetLibVersion": ([c_char_p, c_uint32_p], None),
        "BL_Connect": ([c_char_p, c_uint8, c_int32_p, KBIO.DEVICE_INFO], None),
        "BL_GetUSBdeviceinfos": ([c_uint32, c_char_p, c_uint32_p, c_char_p, c_uint32_p, c_char_p, c_uint32_p], c_bool),
        "BL_Disconnect": ([c_int32], None),
        "BL_TestConnection": ([c_int32], None),
        "BL_TestCommSpeed": ([c_int32, c_uint8, c_int32_p, c_int32_p], None),
        "BL_GetChannelsPlugged": ([c_int32, KBIO.ChannelsArray, c_uint8], None),
        "BL_LoadFirmware": ([c_int32, KBIO.ChannelsArray, KBIO.ResultsArray, c_uint8, c_bool, c_bool, c_char_p, c_char_p], None),
        "BL_GetChannelInfos": ([c_int32, c_uint8, KBIO.CH_INFO], None),
        "BL_GetHardConf": ([c_int32, c_uint8, KBIO.HW_CONF], None),
        "BL_SetHardConf": ([c_int32, c_uint8, KBIO.HardwareConf], None),
        "BL_GetErrorMsg": ([c_int32, c_char_p, c_uint32_p], int),
        "BL_GetOptErr": ([c_int32, c_int8, c_int32_p, c_int32_p], None),
        "BL_GetMessage": ([c_int32, c_uint8, c_char_p, c_uint32_p], None),
        "BL_LoadTechnique": ([c_int32, c_uint8, c_char_p, KBIO.EccParams, c_bool, c_bool, c_bool], None),
        "BL_DefineBoolParameter": ([c_char_p, c_bool, c_int32, KBIO.ECC_PARM], None),
        "BL_DefineSglParameter": ([c_char_p, c_float, c_int32, KBIO.ECC_PARM], None),
        "BL_DefineIntParameter": ([c_char_p, c_int32, c_int32, KBIO.ECC_PARM], None),
        "BL_UpdateParameters": ([c_int32, c_int8, c_int32, KBIO.ECC_PARMS, c_char_p], None),
        "BL_GetParamInfos": ([c_int32, c_int8, c_int32, KBIO.TECHNIQUE_INFOS], None),
        "BL_GetTechniqueInfos": ([c_int32, c_int8, c_int32, KBIO.TECHNIQUE_INFOS], None),
        "BL_StartChannel": ([c_int32, c_int8], None),
        "BL_StartChannels": ([c_int32, KBIO.ChannelsArray, KBIO.ResultsArray, c_uint8], None),
        "BL_StopChannel": ([c_int32, c_int8], None),
        "BL_StopChannels": ([c_int32, KBIO.ChannelsArray, KBIO.ResultsArray, c_uint8], None),
        "BL_GetCurrentValues": ([c_int32, c_int8, KBIO.CURRENT_VALUES], None),
        "BL_GetData": ([c_int32, c_int8, KBIO.DataBuffer, KBIO.DATA_INFO, KBIO.CURRENT_VALUES], None),
        "BL_ConvertNumericIntoSingle": ([c_uint32, c_float_p], None)
    }

    def __init__(self, binary_path: Path):

        dll_path: Path = self._get_dll_file(binary_path)
        self.callable_functions: dict = self._bind_dll_functions(dll_path)

    def __call__(self, function_name: str, *args) -> Any:
        """
        External call of a DLL function by its function name (via the self.callable_functions dictionary).
        Returns the return value of the DLL function.

        Args:
            function_name: Name of the function to be called
            *args: Arguments passed to the function (must match the C++ signature).

        Returns:
            Return value of the function.
        """
        return self.callable_functions[function_name](*args)

    def _get_dll_file(self, binary_path: Path) -> Path:
        """
        Method to get the correct EClib dll file, depending on the bit mode of the system.

        Args:
            binary_path: Path to the directory where the binaries are located.

        Returns:
            Path to the correct EClib dll file.
        """
        bit_mode: int = get_bit_mode()
        return binary_path / self.dll_files[bit_mode]

    def _bind_dll_functions(self, dll_file: Path) -> dict:
        """
        Binds all DLL functions from class variable into a dictionary with function names as keys.

        Args:
            dll_file: Path to the eclib dll file.

        Returns:
            callable_functions: Dictionary of function names and callable
        """
        callable_functions: dict = {}
        dll: ctypes.WinDLL = WinDLL(str(dll_file))

        for func_name, parameters in zip(self.eclib_functions, self.eclib_functions.values()):
            function = dll[func_name]
            function.argtypes = parameters[0]
            callable_functions[func_name] = function

        # TODO: Include function sanity checks (i.e. if result code is 0) and implement appropriate error handling.

        return callable_functions
