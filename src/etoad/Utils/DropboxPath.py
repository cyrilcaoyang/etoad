from pathlib import Path


def get_dropbox_path() -> Path:
    for directory in Path(__file__).parents:
        if "Dropbox" in directory.name:
            return directory