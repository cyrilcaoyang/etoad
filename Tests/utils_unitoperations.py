from typing import Any
from etoad.Interface import GraphicalInterface
from .utils_makeobjects import mk_potentiostat, mk_analyzer


def do_experiment(
        logger: GraphicalInterface,
        technique: str,
        channel: int,
        measurement_settings: dict,
) -> Any:

    potentiostat = mk_potentiostat(logger=logger, channel=channel, sim=False)
    measure_results = potentiostat.do_measurement(
        technique=technique,
        set_parameters=measurement_settings,
        channel=channel
    )
    potentiostat.disconnect()
    return measure_results


def do_analysis(
        logger: GraphicalInterface,
        technique: str,
        analysis_settings: dict,
        results: Any
) -> Any:

    analyzer = mk_analyzer(logger=logger)
    analysis_result = analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique=technique,
        analysis_settings=analysis_settings,
        raw_data=results
    )
    return analysis_result


def cyclic_swv_voltage_parser(
    v_init: float,  # Initial Voltage in V
    v_fin: float,  # Final Voltage in V
    cycle_num: int,  # Number of cycles
) -> (list, list) :

    list_v_init = []
    list_v_fin = []

    for i in range(2 * cycle_num):
        list_v_init.append(v_init) if i % 2 == 0 else list_v_init.append(v_fin)
        list_v_fin.append(v_fin) if i % 2 == 0 else list_v_fin.append(v_init)

    return list_v_init, list_v_fin





