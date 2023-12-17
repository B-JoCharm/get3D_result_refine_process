import os
import shutil
import numpy as np
import math
import json
from meshstat import *

def get_last_folder_name(directory_path):
    normalized_path = os.path.normpath(directory_path)
    last_folder_name = os.path.basename(normalized_path)
    return last_folder_name

def create_folder(base_path, folder_name):
    folder_path = os.path.join(base_path, folder_name)

    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Existing folder removed: {folder_path}")

    os.makedirs(folder_path)
    print(f"New folder created: {folder_path}")

    return folder_path

if __name__ == "__main__":

    crrent_path = os.path.dirname(os.path.realpath(__file__))
    directory_path = os.path.join(crrent_path, 'models\\chai')
    base_path = os.path.join(crrent_path, 'data')
    folder_name = get_last_folder_name(directory_path)

    if not os.path.exists(directory_path):
        print(f"Directory does not exist: {directory_path}")
    else:
        save_path = create_folder(base_path, folder_name)
        num_of_file = len([file for file in os.listdir(directory_path) if file.endswith('.obj')])
        count = 0

        for filename in os.listdir(directory_path):
            if filename.endswith('.obj'):
                file_path = os.path.join(directory_path, filename)
                save_status(file_path, save_path, False, True)
                count += 1
                print("{} / {} obj file is complete".format(count, num_of_file))
