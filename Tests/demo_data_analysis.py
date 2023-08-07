import numpy as np

from etoad.DataAnalyzer import DataAnalyzer
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime, get_dropbox_path
import pickle
from pathlib import Path

PARENT_DIR = Path(__file__).parent
DROPBOX_DIR = get_dropbox_path() / "PythonScript" / "EChem"

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "test_settings" / "logger_settings.json",
    log_file=DROPBOX_DIR / "Logs" / f"{timestamp_datetime()}_data_analysis.log"
    )

# Example A
# Analyzing a multi-iteration CV experiment, and plotting the peak position vs scan rates.

Analyze_CV: bool = True

if Analyze_CV:
    data_analyzer: DataAnalyzer = DataAnalyzer(PARENT_DIR / "test_files", logger=logger)
    data_analyzer.analyze_data(
        sample_name="analysis_CV_scans",
        experiment_name="test",
        technique="CV",
        analysis_settings={
            "Plot": {"title": "Test CV Measurement"},
            "Peak Picking": {},
            "Integration": {},
            "Peaks Scanrate": {}
        },
        raw_data=np.load(PARENT_DIR / "test_files" / "Test_Multi_CV.pkl", allow_pickle=True)
    )

# Example B
# Analyzing a cyclic SWV experiment, and plot the intergrated area.

Analyze_Cyclic_SWV: bool = False

if Analyze_Cyclic_SWV:
    data_analyzer: DataAnalyzer = DataAnalyzer(PARENT_DIR / "test_files", logger=logger)
    data_analyzer.analyze_data(
        sample_name="analysis_SWV_scans",
        experiment_name="test",
        technique="SWV",
        analysis_settings={
            "Plot": {"title": "Test Multi-SWV Measurement"},
            "Peak Picking": {},
            "CV Parameters": {},
            "Integration": {}
        },
        raw_data=np.load(PARENT_DIR / "test_files" / "Test_Cyclic_SWV.pkl", allow_pickle=True)
    )
