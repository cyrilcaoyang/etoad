from Drivers import EChemController

controller = EChemController(
    server="USB0",
    channel=2
)

controller.stop_channel()

