from pathlib import Path


def data_path():
    """
    Returns:
        The paths of the test folder and data folder
    """
    parent_dir = Path(__file__).parent.parent
    data_dir = Path("C://Users//Prep LC//Desktop//AutoEChem_Data")
    return parent_dir, data_dir
