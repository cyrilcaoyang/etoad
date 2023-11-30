from etoad.Interface import GraphicalInterface
from .utils_makeobjects import mk_potentiostat, mk_analyzer


def measure_plot_ocv(
        logger: GraphicalInterface,
        para: tuple = (10, 0.1, 0.05, 4),
        channel: int = 1,
        simulation_opt: bool = False,
) -> dict:

    potentiostat = mk_potentiostat(logger=logger, channel=channel, sim=simulation_opt)
    results = potentiostat.do_measurement(
        technique="OCV",
        set_parameters={
            "IterationSettings": {
                "no_iterations": para[3]
            },
            "TechniqueParameters": {
                "Voltage Interval Size": {"value": para[1]},
                "Time Interval Size": {"value": para[2]},
                "Rest Time": {"value": para[0]}
            }
        }
    )

    analyzer = mk_analyzer(logger=logger)
    analysis_result = analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="OCV",
        analysis_settings={
            "Plot": {"title": f"OCV for {para[3]} seconds"},
            "Voltage": {}
        },
        raw_data=results,
    )
    logger.stop_gui()
    return analysis_result


def measure_swv(
    logger: GraphicalInterface,
    para_range_time: tuple,
    para_pulse: tuple = (0.025, 0.200, 0.010, 0.800),
    channel: int = 1,
    simulation_opt: bool = False
) -> dict:

    potentiostat = mk_potentiostat(logger=logger, channel=channel, sim=simulation_opt)
    results = potentiostat.do_measurement(
        technique="SWV",
        set_parameters={
            "IterationSettings": {"no_iterations": 1},
            "TechniqueParameters": {
                "Initial Voltage": {"value": para_range_time[0]},
                "Final Voltage": {"value": para_range_time[1]},
                "Rest Time": {"value": para_range_time[2]},
                "Pulse Height": {"value": para_pulse[0]},
                "Pulse Width": {"value": para_pulse[1]},
                "Step Height": {"value": para_pulse[2]},
                "Start Averaging Interval": {"value": para_pulse[3]}
            }
        },
        channel=channel
    )
    potentiostat.disconnect()
    return results

