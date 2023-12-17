import os
import sys
import bpy
import bmesh
import math
import mathutils
script_directory = os.path.dirname(os.path.realpath(__file__))
if script_directory not in sys.path:
    sys.path.append(script_directory)

from script.remove_internal import *
from script.merge_edge import *
from script.blender_modifier import *
from script.remove_connected_components import *
from script.remove_boundary_loops import *
from script.remove_edges_not_include_face import *
from script.remake_texture_uv import *
from script.dissolve_manifold_vertex import *
from model_setting import *
from script.subdivide_polygon import *
from script.make_manifold import *
from script.saliency_high_smoothing import *




# 전달받은 인자로 디렉토리 및 파일 이름 설정
# main스크립트의 맨 마지막 subprocess.run 구문에서 맨 오른쪽 변수(경로)가 sys.argv[-1]
modelPath = sys.argv[-3] + "\\"
model_name = sys.argv[-2]
output_directory = sys.argv[-1]

# 입력 파일 경로 설정
obj_file = modelPath + model_name + ".obj"
mtl_file = modelPath + model_name + ".mtl"
texture_file = modelPath + model_name + ".png"

# 기본으로 있는 큐브 오브젝트 삭제
cube = bpy.data.objects.get("Cube")
if cube:
    bpy.ops.object.select_all(action='DESELECT')
    cube.select_set(True)
    bpy.ops.object.delete()

# 메시 불러오기 및 초기설정 
imported_objs = mesh_initial_setting(obj_file, texture_file)

# obj 선택 
obj = bpy.context.active_object


############################ 개선 스크립트 ##############################

# 임계점 이하 엣지 병합 ( target < 평균 * gamma ) 
merge_edge(obj, gamma = 0.1)

# 연결요소 제거
remove_connected_components(obj, 0.1)

# 미러 모디파이어 적용
mirror_modifier(obj)

# 내부 요소 제거
remove_internal_vertices(obj)

# 연결요소 제거 ( 한번 더? 안할수도 )
remove_connected_components(obj, 0.9)

# 삼각 분할 모디파이어 적용
triangulate_modifier(obj)

# ---------------- 메쉬 최적화 완료 --------------------


# -------------- 연결성 및 무결성 완료 ------------------

# 텍스쳐 UV 매핑 및 Bake
remake_texture_uv(model_name, output_directory)

# -------------- 텍스처 및 UV 매핑 완료 -----------------

# 데시메이트
decimate_modifier(obj, ratio = 0.99)

# saliency가 높은부분 제외하고 스무딩 ( 메쉬의 디테일을 살리는 부분 )
saliency_based_smoothing(obj, saliency_threshold = 0.25, smoothingIteration = 30,lambda_factor = 0.1)

# 라플라시안 스무딩 모디파이어 적용
laplacian_smoothing_modifier(obj, 10, 0.1)

# 매니폴드 만들기
make_manifold(obj)
make_manifold(obj)

# 삼각 분할 모디파이어 적용
triangulate_modifier(obj)

# -------------- 메쉬 부드럽게 만들기 완료 ---------------

###########################################################################


# Make sure the object's name does not contain invalid characters for a filename
safe_obj_name = "".join([c for c in obj.name if c.isalpha() or c.isdigit() or c==' ']).rstrip()

# Set the OBJ and MTL file paths
obj_file_path = os.path.join(output_directory, f"{safe_obj_name}.obj")
mtl_file_path = os.path.join(output_directory, f"{safe_obj_name}.mtl")

# 개선된 메시 정보 저장 
bpy.ops.export_scene.obj(
    filepath= obj_file_path,
    use_selection=True,
    use_materials=True,
    path_mode='COPY'
)

# 블렌더 종료
bpy.ops.wm.quit_blender()
