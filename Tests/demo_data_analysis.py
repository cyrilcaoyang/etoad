import numpy as np

from etoad.DataAnalyzer import DataAnalyzer
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime
from pathlib import Path

"""
    This python script test the DataAnalyzer Module.
    Two example are provided in the /analyzer_test folder.
    The first one analyze a csv file, while the second one reads a pickle file.
"""

PARENT_DIR = Path(__file__).parent
with open(PARENT_DIR / "test_settings" / "data_settings") as file:
    DATA_DIR = Path(file.read())

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "test_settings" / "logger_settings.json",
    log_file=DATA_DIR / "Logs" / f"{timestamp_datetime()}_data_analysis.log"
    )

# Example A
# Analyzing a multi-iteration CV experiment, and plotting the peak position vs scan rates.

Analyze_CV: bool = True

if Analyze_CV:
    data_analyzer: DataAnalyzer = DataAnalyzer(PARENT_DIR / "analyzer_test", logger=logger)
    data_analyzer.analyze_data(
        sample_name="K4[Fe(CN)6]",
        experiment_name="CV_const_ScanRate",
        technique="CV",
        analysis_settings={
            "Plot": {"title": "Test CV Measurement"},
            "Peak Picking": {},
            "Integration": {}
            # "Peaks Scanrate": {}
        },
        raw_data=np.genfromtxt(PARENT_DIR / "analyzer_test" / "CV_K4[Fe(CN)6]-smooth_23-08-31_16-02.csv", delimiter=',')
    )

# Example B
# Analyzing a cyclic SWV experiment, and plot the intergrated area.

Analyze_Cyclic_SWV: bool = False

if Analyze_Cyclic_SWV:
    data_analyzer: DataAnalyzer = DataAnalyzer(PARENT_DIR / "analyzer_test", logger=logger)
    data_analyzer.analyze_data(
        sample_name="K4[Fe(CN)6]",
        experiment_name="SWV_Multi_Scans",
        technique="SWV",
        analysis_settings={
            "Plot": {"title": "Test Multi-SWV Measurement"},
            "Peak Picking": {},
            "CV Parameters": {},
            "Integration": {}
        },
        raw_data=np.load(PARENT_DIR / "analyzer_test" / "Test_Cyclic_SWV.pkl", allow_pickle=True)
    )
