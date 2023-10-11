import pprint
from pathlib import Path
from typing import Union, Tuple, Dict
from logging import Logger
import matplotlib.figure
import numpy as np

from etoad.Utils import timestamp_datetime
from etoad.Utils import save_as_csv, save_as_json
from etoad.Utils import log_exceptions
from etoad.DataAnalyzer.Methods import CVAnalyzer, PulseTechniqueAnalyzer, OCVAnalyzer, EChemDataAnalyzer


class DataAnalyzer:
    """
    Minimum viable version of a DataAnalyzer for Electrochemical Data
    """

    _technique_analyzers: dict = {
        "CV": CVAnalyzer,
        "SWV": PulseTechniqueAnalyzer,
        "DPV": PulseTechniqueAnalyzer,
        "OCV": OCVAnalyzer,
    }

    def __init__(
            self,
            data_path: Path,
            logger: Logger
    ):
        """
        Instantiates the general data analyzer.

        Args:
            data_path: Path to the folder where experimental data is stored.
            logger: Logger object
        """
        self._data_path: Path = data_path
        self.logger: Logger = logger

    @log_exceptions
    def analyze_data(
            self,
            sample_name: str,
            experiment_name: str,
            technique: str,
            analysis_settings: dict,
            raw_data: np.ndarray,
    ) -> Dict[str, Union[list, dict]]:
        """
        Public method to run the data for a specific electrochemical measurement technique.
        Instantiates the analyzer object for the specific technique and runs the data analysis.

        Args:
            sample_name: Name of the sample to be measured.
            experiment_name: Name of the specific experiment performed.
            technique: Name of the experimental technique.
            analysis_settings: Dictionary of keywords and specifications for data analysis for the specific technique.
            raw_data: Numpy ndarray of the obtained raw data.

        Returns:
            analysis_results: Dictionary of all analysis results returned by the EChemAnalyzer
        """
        sample_dir, basename = self._get_target_folder(sample_name, experiment_name)
        self._save_raw_data(raw_data, sample_dir, basename)     # Saves the raw data in case the analysis fails

        analyzer: EChemDataAnalyzer = self._technique_analyzers[technique](
            analysis_settings=analysis_settings,
            raw_data=raw_data,
            logger=self.logger
        )

        analysis_results, figures = analyzer.run_analysis()
        self.logger.debug(f"Data Analysis Completed:\n {pprint.pformat(analysis_results)}")  # pprint is prettier :)
        self._save_analyzed_data(analysis_results, figures, sample_dir, basename)     # Saves the analysis results

        return analysis_results

    def _get_target_folder(
            self,
            sample_name: str,
            experiment_name: str
    ) -> Tuple[Path, str]:
        """
        Sets up the target folder for saving experimental results.

        Args:
            sample_name: Name of the sample to be measured.
            experiment_name: Name of the specific experiment performed.

        Returns:
            sample_dir: Path to the sample-specific data directory.
            file_basename: Basename of the specific experiment ($NAME_$EXP_$TIME)
        """
        sample_dir = self._data_path / sample_name
        sample_dir.mkdir(parents=True, exist_ok=True)

        file_basename = f"{sample_name}_{timestamp_datetime()}_{experiment_name}"
        return sample_dir, file_basename

    @log_exceptions
    def _save_raw_data(
            self,
            raw_data: np.ndarray,
            sample_dir: Path,
            file_basename: str
    ) -> None:
        """
        Saves the experimental results (raw data and analysis results as .csv) into the target folder.

        Args:
            raw_data: Numpy ndarray of the obtained raw data.
            sample_dir: Path to the sample-specific data directory.
        """
        save_as_csv(raw_data, sample_dir / f"{file_basename}.csv")
        self.logger.info(f"Raw data was saved to {sample_dir / f'{file_basename}.csv'}")

    @log_exceptions
    def _save_analyzed_data(
            self,
            analysis_results: Dict[str, Union[list, dict]],
            figures: Dict[str, matplotlib.figure.Figure],
            sample_dir: Path,
            file_basename: str
    ) -> None:
        """
        Saves the experimental results (raw data as .pkl and analysis results as .csv) into the target folder.

        Args:
            analysis_results: Dictionary of all analysis results saved by the EChemAnalyzer
            figures: Dictionary of all figures created by the EChemAnalyzer
            sample_dir: Path to the sample-specific data directory.
        """

        save_as_json(analysis_results, sample_dir / f"{file_basename}_analysis.json")
        self.logger.info(f"Analysis results were saved to {sample_dir / f'{file_basename}_analysis.json'}")

        for fig_name, figure in zip(figures, figures.values()):
            figure.savefig(sample_dir / f"{file_basename}_{fig_name}.png", transparent=True, dpi=600)
