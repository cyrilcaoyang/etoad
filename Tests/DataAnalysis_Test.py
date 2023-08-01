import numpy as np

from etoad.DataAnalyzer import DataAnalyzer
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime, get_dropbox_path
import pickle
from pathlib import Path

PARENT_DIR = get_dropbox_path() / "PythonScript" / "EChem" / "Settings"

logger = GraphicalInterface(
    logging_config=PARENT_DIR / "logger_settings_v2.json",
    log_file=PARENT_DIR / "logs" / f"Test_data_analysis_{timestamp_datetime()}.log"
    )

# data_analyzer: DataAnalyzer = DataAnalyzer(Path(r"C:\Users\Potentiostat_SP-300\Desktop\The Matter Lab\Test_Data"),logger=logger)
# data_analyzer.analyze_data(
#     sample_name="test1",
#     experiment_name="test",
#     technique="CV",
#     analysis_settings={
#         "Plot": {"title": "Test CV Measurement"},
#         "Peak Picking": {},
#         "Integration": {},
#         "Peaks Scanrate": {}
#
#     },
#     raw_data=np.load(r"C:\Users\Lenovo\Desktop\The Matter Lab\python_echem\Test_Multi_CV.pkl", allow_pickle=True)
# )

data_analyzer: DataAnalyzer = DataAnalyzer(Path(__file__).parent / "test_files", logger=logger)
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
    raw_data=np.load(Path(__file__).parent/ "test_files" /"Test_Cyclic_SWV.pkl", allow_pickle=True)
)
