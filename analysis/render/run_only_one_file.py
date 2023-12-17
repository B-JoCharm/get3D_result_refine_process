import os
import tkinter as tk
from tkinter import filedialog
import shutil
import subprocess

# 파일 탐색기를 열어 .obj 파일 선택
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(filetypes=[("OBJ files", "*.obj")])

# 파일 이름 및 디렉토리 추출
model_path, full_model_name = os.path.split(file_path)
model_name, _ = os.path.splitext(full_model_name)

script_directory = os.path.dirname(os.path.realpath(__file__))
output_directory = os.path.join(script_directory, "output")
os.makedirs(output_directory, exist_ok=True)

#선택된 obj파일과 동명인 디렉토리 생성
selected_obj_folder = os.path.join(output_directory, model_name)
if os.path.exists(selected_obj_folder):
    shutil.rmtree(selected_obj_folder)
os.makedirs(selected_obj_folder)

# 렌더링된 결과물들을 저장할 origin_rendering_output 생성
rendering_output = os.path.join(selected_obj_folder, "rendering_output")

if os.path.exists(rendering_output):
    shutil.rmtree(rendering_output)

os.makedirs(rendering_output)

# curvSaliency를 매핑한 모델의 렌더링된 결과물들을 저장할 curvSal_rendering_output 생성
mesh_saliency_rendering_output = os.path.join(selected_obj_folder, "mesh_saliency_rendering_output")

if os.path.exists(mesh_saliency_rendering_output):
    shutil.rmtree(mesh_saliency_rendering_output)

os.makedirs(mesh_saliency_rendering_output)

#----------------------------------필요한 파일 생성 끝----------------------------------------

# .bat 파일을 실행하면서 선택한 obj 파일의 경로, 파일 이름, 출력 디렉토리 경로를 인자로 전달
# 3Drender.py 스크립트를 백그라운드에서 블렌더를 통해 실행시키기 위함
bat_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "run_blender.bat")
subprocess.run([bat_file_path, model_path, model_name, rendering_output, mesh_saliency_rendering_output], check=True)
