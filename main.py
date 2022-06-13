import numpy as np
from Potentiostat import EChemController
from Utils.PreliminaryDataHandling import scatter_plot, save_data

from ExampleSettings.CV_Parameters import CV_PARAMETERS
from ExampleSettings.SWV_Parameters import SWV_PARAMETERS
from ExampleSettings.DPV_Parameters import DPV_PARAMETERS

controller = EChemController(
    server="USB0",
    channel=2,
)

controller.load_technique(
    technique="DPV",
    parameters=DPV_PARAMETERS
)

results: np.ndarray = controller.do_measurement()

scatter_plot(results[:, 1], results[:, 2])
