import os
import tkinter as tk
from tkinter import filedialog
import shutil
import subprocess
from meshstat import *

def improve_obj_files_in_folder():
    # 폴더 선택
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()

    # 폴더 내 모든 .obj 파일 찾기
    obj_files = [f for f in os.listdir(folder_path) if f.endswith('.obj')]

    # 각 .obj 파일에 대한 작업 수행
    for file in obj_files:
        improve_single_obj_file(folder_path, file)

def improve_single_obj_file(folder_path, file_name):
    # 파일 이름 및 디렉토리 추출
    model_name, _ = os.path.splitext(file_name)

    # output 디렉토리 설정
    script_directory = os.path.dirname(os.path.realpath(__file__))
    output_directory = os.path.join(script_directory, "output")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)

    # 선택된 obj 파일과 동명의 디렉토리 생성
    selected_obj_folder = os.path.join(output_directory, model_name)
    if os.path.exists(selected_obj_folder):
        shutil.rmtree(selected_obj_folder)
    os.makedirs(selected_obj_folder)

    # .bat 파일 실행
    bat_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "run_blender.bat")
    subprocess.run([bat_file_path, folder_path, model_name, selected_obj_folder], check=True)

    # 모델 통계 저장
    improve_model = model_name + ".obj"
    obj_path = os.path.join(selected_obj_folder, improve_model)
    save_status(obj_path, selected_obj_folder, save_txt=True, save_data=True)
    print("model : {} is complete!".format(model_name))

# 함수 호출
improve_obj_files_in_folder()