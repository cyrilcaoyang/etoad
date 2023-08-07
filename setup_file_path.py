import os
from pathlib import Path

"""
    This file set up the folder path in which data will be stored.
    Add settings for the location of data storage, write into /test_settings/file_settings    
    Please note:
    Cloud-synchronized folders by DropBox, OneDrive, or GoogleDrive, are NOT recommanded.
    They might cause issues during syncing.
"""
# TODO: Remove the need for DropboxPath.py

PARENT_PATH = Path(__file__).parent


def get_user_path():

    data_path = PARENT_PATH / "Data"

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
            if _exit == 'E':
                exit()


if __name__ == "__main__":

    print("Thanks for choosing eTOAD!\n Now please configure Data Storage for me :) ")
    user_path = get_user_path()
    setting_path = PARENT_PATH / "Tests" / "test_settings" / "file_settings"

    with open(setting_path, "w") as file_settings:
        file_settings.write(str(user_path))

    print(f"Data Storage path set to: {user_path}.")
    print(f"Configuration saved to {setting_path}.")
