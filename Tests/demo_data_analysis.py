import numpy as np

from etoad.DataAnalyzer import DataAnalyzer
from etoad.Interface import GraphicalInterface
from etoad.Utils import timestamp_datetime
from test_utils import DataPath

"""
    This python script test the DataAnalyzer Module.
    Two example are provided in the /analyzer_test folder.
    The first one analyze a csv file, while the second one reads a pickle file.
"""

# Example
# Analyzing a multi-iteration CV experiment, and plotting the peak position vs scan rates.

if __name__ == "__main__":

    PARENT_DIR, DATA_DIR = DataPath.data_path()

    logger = GraphicalInterface(
        logging_config=PARENT_DIR / "test_settings" / "logger_settings.yaml",
        log_file=DATA_DIR / "Logs" / f"{timestamp_datetime()}_data_analysis.log"
    )

    data_analyzer: DataAnalyzer = DataAnalyzer(PARENT_DIR / "analyzer_test", logger=logger)
    data_analyzer.analyze_data(
        sample_name="K4[Fe(CN)6]",
        experiment_name="CV_const_ScanRate",
        technique="CV",
        analysis_settings={
            "Plot": {"title": "Test CV Measurement"},
            "Peak Picking": {},
            "Peaks Scanrate": {},
            "Currents Scanrate": {}
        },

        # Analyze a csv file
        raw_data=np.genfromtxt(
            "C:/Users/Prep LC/Desktop/AutoEChem_Data/DATA/K4[Fe(CN)6]-cv-peak-scanrate/K4[Fe(CN)6]_23-09-21_16-34_CV.csv",
            delimiter=',')

        # Analyze a pickle file
        # raw_data=np.load(PARENT_DIR / "analyzer_test" / "Test_Cyclic_SWV.pkl", allow_pickle=True)

    )
#