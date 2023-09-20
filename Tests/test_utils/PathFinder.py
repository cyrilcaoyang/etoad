from pathlib import Path


def data_path():
    """
    Returns:
        The paths of the test folder and data folder
    """
    parent_dir = Path(__file__).parent.parent
    with open(parent_dir / "test_settings" / "data_settings") as file:
        data_dir = Path(file.read())
    return parent_dir, data_dir
