from Drivers import EChemController
from Drivers.Utils import scatter_plot

from ExampleSettings.CV_Parameters import CV_PARAMETERS
from ExampleSettings.SWV_Parameters import SWV_PARAMETERS


controller = EChemController(
    server="USB0",
    channel=2,
)

controller.load_technique(
    technique="SWV",
    parameters=SWV_PARAMETERS
)

results = controller.do_measurement()
scatter_plot(results[:, 1], results[:, 2])

