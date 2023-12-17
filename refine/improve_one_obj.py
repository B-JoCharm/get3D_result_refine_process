import os
import tkinter as tk
from tkinter import filedialog
import shutil
import subprocess
from meshstat import *
from quality_comparison import *

# 파일 탐색기를 열어 .obj 파일 선택
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(filetypes=[("OBJ files", "*.obj")])

# 파일 이름 및 디렉토리 추출
model_path, full_model_name = os.path.split(file_path)
model_name, _ = os.path.splitext(full_model_name)

# output디렉토리가 존재하지 않는다면 생성
script_directory = os.path.dirname(os.path.realpath(__file__))
output_directory = os.path.join(script_directory, "output")
if not os.path.exists(output_directory):
    os.makedirs(output_directory, exist_ok=True)

# output 디렉토리안에 선택된 obj파일과 동명인 디렉토리 생성
selected_obj_folder = os.path.join(output_directory, model_name)
if os.path.exists(selected_obj_folder):
    shutil.rmtree(selected_obj_folder)
os.makedirs(selected_obj_folder)

#----------------------------------필요한 파일 생성 끝----------------------------------------

# .bat 파일을 실행하면서 선택한 obj 파일의 경로, 파일 이름, 출력 디렉토리 경로를 인자로 전달
# 3Drender.py 스크립트를 백그라운드에서 블렌더를 통해 실행시키기 위함
bat_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "run_blender.bat")
# run_blender.py에서 맨 오른쪽부터 -1로 사용 (bat_file_path은 bat파일 실행을 위한거라 제외)
subprocess.run([bat_file_path, model_path, model_name, selected_obj_folder], check=True)

improve_model = model_name + ".obj"
obj_path = os.path.join(selected_obj_folder, improve_model)

original_data = save_status(file_path, selected_obj_folder, save_txt = False , save_data = True)
refine_data = save_status(obj_path, selected_obj_folder, save_txt = True , save_data = True)

save_comparison_data(original_data, refine_data, selected_obj_folder, model_name)

print("model : {} is complete!".format(model_name))
