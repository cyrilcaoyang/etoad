import numpy as np

from etoad.DataAnalyzer import DataAnalyzer
from etoad.DataAnalyzer.Methods import OCVAnalyzer
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime
from pathlib import Path
from test_utils import DataPath

"""
    This python script test the DataAnalyzer Module.
    Two example are provided in the /analyzer_test folder.
    The first one analyze a csv file, while the second one reads a pickle file.
"""

PARENT_DIR, DATA_DIR = DataPath.data_path()

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "test_settings" / "logger_settings.yaml",
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
            "Integration": {},
            "Currents Scanrate": {}
        },
        raw_data=np.genfromtxt(
            "C:/Users/Prep LC/Desktop/AutoEChem_Data/DATA/K4[Fe(CN)6]-cv-peak-scanrate/K4[Fe(CN)6]_23-09-21_16-34_CV.csv",
            delimiter=','
        )
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

# Example C
# Analyzing OCV experiment, and plot the data.

Analyze_OCV: bool = False

if Analyze_OCV:
    data_analyzer: DataAnalyzer = DataAnalyzer(PARENT_DIR / "analyzer_test", logger=logger)
    data_analyzer.analyze_data(
        sample_name="K4[Fe(CN)6]",
        experiment_name="OCV scan",
        technique="OCV",
        analysis_settings={
            "Plot": {},
        },
        raw_data=np.genfromtxt(PARENT_DIR / "analyzer_test" / "Open Circuit Voltammetry_K4[Fe(CN)6]-OCV_23-09-06_17-59-2.csv", delimiter=',')
    )
