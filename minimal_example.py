__author__ = "Felix Strieth-Kalthoff (felix-s-k)"
"""
Minimal Example for Usage of the BL_LoadFirmware Function 
"""
import sys
from typing import Callable
from pathlib import Path
from ctypes import *
import logging

development_package: Path = Path(r"C:\EC-Lab Development Package")
python_helpers = development_package / "Examples" / "Python"
sys.path.append(str(python_helpers))
import kbio
from kbio.c_utils import c_int32_p
from kbio.kbio_types import DeviceInfo, DEVICE_INFO, ChannelsArray, ChannelInfo, CH_INFO,  MAX_SLOT_NB
from kbio.kbio_types import EccParam, ECC_PARM, ECC_PARM_ARRAY, EccParams
from kbio.kbio_types import ResultsArray

# Paths to Binaries, DLL and Firmware Files
binaries: Path = development_package / "EC-Lab Development Package"
dll_file: Path = binaries / "EClib64.dll"
bin_file: Path = binaries / "kernel4.bin"
# bin_file: str = "kernel4.bin"
# bin_file = None
xlx_file: Path = binaries / "Vmp_iv_0395_aa.xlx"
# xlx_file: str = "Vmp_iv_0395_aa.xlx"
# xlx_file = None
cv_file: Path = binaries / "cv4.ecc"

# Global Variables, Parameters and Settings
port: str = "USB0"
timeout: int = 5
channels: list = [0, 1]
loaded_via_ec_lab_express: bool = False

# Setup logging and log some basic information
logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(filename="LoadFirmwareTest.log", encoding="utf8", level=logging.INFO, format="%(asctime)s %(message)s")
logging.info("TESTS OF LOADING THE FIRMWARE TO THE POTENTIOSTAT")
logging.info("Instrument: SP-300")
logging.info("Development Package: Version 6.04 –May 2021")
logging.info(f"Manual Loading of Firmware via EC-Lab Express: {loaded_via_ec_lab_express}")
logging.info(f"DLL File: {dll_file}")
logging.info(f"BIN File (loaded via Python): {bin_file}")
logging.info(f"XLX File (loaded via Python): {xlx_file}")


# Load and bind required DLLs
dll: WinDLL = WinDLL(str(dll_file))

BL_Connect: Callable = dll["BL_Connect"]
BL_Connect.argtypes = [c_char_p, c_uint8, c_int32_p, DEVICE_INFO]

BL_LoadFirmware: Callable = dll["BL_LoadFirmware"]
BL_LoadFirmware.argtypes = [c_int32, ChannelsArray, ResultsArray, c_uint8, c_bool, c_bool, c_char_p, c_char_p]

BL_GetChannelInfos: Callable = dll["BL_GetChannelInfos"]
BL_GetChannelInfos.argtypes = [c_int32, c_uint8, CH_INFO]

BL_DefineIntParameter: Callable = dll["BL_DefineIntParameter"]
BL_DefineIntParameter.argtypes = [c_char_p, c_int32, c_int32, ECC_PARM]

BL_DefineSglParameter: Callable = dll["BL_DefineSglParameter"]
BL_DefineSglParameter.argtypes = [c_char_p, c_float, c_int32, ECC_PARM]

BL_DefineBoolParameter: Callable = dll["BL_DefineBoolParameter"]
BL_DefineBoolParameter.argtypes = [c_char_p, c_bool, c_int32, ECC_PARM]

BL_LoadTechnique: Callable = dll["BL_LoadTechnique"]
BL_LoadTechnique.argtypes = [c_int32, c_uint8, c_char_p, EccParams, c_bool, c_bool, c_bool]

BL_StartChannel: Callable = dll["BL_StartChannel"]
BL_StartChannel.argtypes = [c_int32, c_int8]

BL_StopChannel: Callable = dll["BL_StopChannel"]
BL_StopChannel.argtypes = [c_int32, c_int8]

BL_Disconnect: Callable = dll["BL_Disconnect"]
BL_Disconnect.argtypes = [c_int32]


# Connect to the device
device_id, device_info = c_int32(), DeviceInfo()
return_value = BL_Connect(port.encode(), timeout, device_id, device_info)
logging.info(f"BL_Connect returned {return_value}.")
logging.info(device_info)

# Load firmware
if not loaded_via_ec_lab_express:
    channels_array, results_array = ChannelsArray(), ResultsArray()
    for channel in channels:
        channels_array[channel] = c_bool(True)
    return_value = BL_LoadFirmware(
        device_id,
        channels_array,
        results_array,
        MAX_SLOT_NB,
        False,
        False,
        str(bin_file).encode(),
        str(xlx_file).encode()
    )
    logging.info(f"BL_LoadFirmware returned {return_value}.")


# Check Channel Infos
for channel in channels:
    channel_info = ChannelInfo()
    return_value = BL_GetChannelInfos(device_id, channel, channel_info)
    logging.info(f"BL_GetChannelInfos returned {return_value} for channel {channel}.")
    logging.info(channel_info)


# Load CV to channel 1
CV_params: list = [
    ("Voltage_step", BL_DefineSglParameter, 0, 0),
    ("Voltage_step", BL_DefineSglParameter, 0, 1),
    ("Voltage_step", BL_DefineSglParameter, -0.5, 2),
    ("Voltage_step", BL_DefineSglParameter, 0, 3),
    ("Voltage_step", BL_DefineSglParameter, 0, 4),
    ("vs_initial", BL_DefineBoolParameter, False, 0),
    ("vs_initial", BL_DefineBoolParameter, False, 1),
    ("vs_initial", BL_DefineBoolParameter, False, 2),
    ("vs_initial", BL_DefineBoolParameter, False, 3),
    ("vs_initial", BL_DefineBoolParameter, False, 4),
    ("Scan_Rate", BL_DefineSglParameter, 0.05, 0),
    ("Scan_Rate", BL_DefineSglParameter, 0.05, 1),
    ("Scan_Rate", BL_DefineSglParameter, 0.05, 2),
    ("Scan_Rate", BL_DefineSglParameter, 0.05, 3),
    ("Scan_Rate", BL_DefineSglParameter, 0.05, 4),
    ("Scan_number", BL_DefineIntParameter, 2, 0),
    ("Record_every_dE", BL_DefineSglParameter, 0.01, 0),
    ("Average_over_dE", BL_DefineBoolParameter, True, 0),
    ("N_Cycles", BL_DefineIntParameter, 1, 0),
    ("Begin_measuring_I", BL_DefineSglParameter, 0, 0),
    ("End_measuring_I", BL_DefineSglParameter, 1.0, 0)
]

no_params: int = len(CV_params)
param_array: Array = ECC_PARM_ARRAY(no_params)

for i, parameter in enumerate(CV_params):
    parameter_object = EccParam()
    parameter[1](parameter[0].encode(), parameter[2], parameter[3], parameter_object)
    param_array[i] = parameter_object

all_parameter_object = EccParams(no_params, param_array)

return_value = BL_LoadTechnique(device_id, 1, str(cv_file).encode(), all_parameter_object, True, True, True)
logging.info(f"BL_LoadTechnique returned {return_value}.")



# Close connection to the instrument
return_value = BL_Disconnect(device_id)
logging.info(f"BL_Disconnect returned {return_value}. \n \n \n")