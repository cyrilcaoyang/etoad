import os
from pathlib import Path

"""
    After installation of eTOAD,
    Run this file to set up the folder path in which experimental data will be stored.
    Add settings for the location of data storage, write into /test_settings/file_settings
"""

PARENT_PATH = Path(__file__).parent


def get_user_path():

    data_path = PARENT_PATH / "Data"

#   You have the option to store the Echem data in the same path of python scripts (NOT recommended).
#   Alternatively, you can specify a new path to desired directory.
#   Please be aware:
#       Cloud-synchronized folders by DropBox, OneDrive, or GoogleDrive, are NOT recommended.
#       They might cause issues during syncing.

    while True:
        choice = input("Would you like to store data in a folder DIFFERENT from the current one?: [Y/N]")
        if choice == 'Y':
            break
        elif choice == 'N':
            return data_path
        else:
            print("You option is invalid, please try again.")

    while True:
        user_path = input("Please enter the desired path to store your data:")
        if os.path.exists(user_path):
            return user_path
        else:
            _exit = input("Entered path does not exist. Please try again, or exit: [E]")
            if _exit == 'E': exit()


if __name__ == "__main__":

    print("Thanks for choosing eTOAD!\n Now please configure data storage for me :) ")
    user_path = get_user_path()
    setting_path = PARENT_PATH / "Tests" / "test_settings" / "file_settings"

    with open(setting_path, "w") as file_settings:
        file_settings.write(str(user_path))

    print(f"Data storage path set to: {user_path}.")
    print(f"Data configuration saved to {setting_path}.")
