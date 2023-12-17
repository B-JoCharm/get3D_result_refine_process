import bpy
import math
import mathutils
import os
import sys
import bmesh
script_directory = os.path.dirname(os.path.realpath(__file__))
if script_directory not in sys.path:
    sys.path.append(script_directory)
from renderMethod import *
from saliencyMethod import *


# 전달받은 인자로 디렉토리 및 파일 이름 설정
modelPath = sys.argv[-4] + "\\"
file_name = sys.argv[-3]
rendering_output_directory = sys.argv[-2]
mesh_saliency_rendering_output_directory = sys.argv[-1]


# 기본으로 있는 큐브 오브젝트 삭제
cube = bpy.data.objects.get("Cube")
if cube:
    bpy.ops.object.select_all(action='DESELECT')
    cube.select_set(True)
    bpy.ops.object.delete()

# 입력 파일 경로 설정 (임의로 본인 컴퓨터의 경로에 맞게 설정)
obj_file = modelPath + file_name + ".obj"
mtl_file = modelPath + file_name + ".mtl"
texture_file = modelPath + file_name + ".png"

# 카메라, 광원 naming
camera = bpy.data.objects.get("Camera")
light = bpy.data.objects.get('Light')

# 초기 위치 및 회전 각도 설정
initial_location = (8, 0, 0)
initial_rotation = (math.radians(90), 0, math.radians(90))

# 렌더링 매개변수 설정
resolution_x = 1920
resolution_y = 1080
samples = 100

# 반복할 각도 간격 설정 (saliency 매핑한 모델을 렌더링 할 때도 사용)
rotateRadius = 90

camera_setting(camera, initial_location, initial_rotation)
light_setting(light, initial_location)

# 메시 불러오기 및 초기설정(불러온 객체 선택 및 활성화, 스케일조정), imported_objs로 선택된 객체 리스트를 반환함에 따라 불러온 객체를 다시 선택할때 사용 가능
imported_objs = mesh_initial_setting(obj_file, texture_file)

# 재질과 텍스처 적용 (텍스처 파일이 있을 경우에만)
if os.path.exists(texture_file):
    apply_mtl_and_texture(texture_file)

# 렌더링 설정 (엔진 : CYCLE)
rendering_setting('CYCLE',resolution_x,resolution_y,samples)

# mesh 렌더링
rendering('mesh',rendering_output_directory, file_name, rotateRadius, camera, light, initial_location)

# ------------------------------------ saliency map을 구해서 jet 컬러맵으로 매핑 -------------------------------------------
obj = bpy.context.active_object
mesh = obj.data
bm = bmesh.new()
bm.from_mesh(mesh)

neighbor_verts_dict = find_neighbors(bm)
curvatures = find_curvature(bm)

# 모델의 경계 상자 대각선 길이를 계산
diagonal_length = calculate_diagonal_length(obj)

# ε 값을 계산 (경계 상자 대각선 길이의 0.3%)
epsilon = 0.003 * diagonal_length

# 다섯 가지 스케일 정의
scales = [2 * epsilon, 3 * epsilon, 4 * epsilon, 5 * epsilon, 6 * epsilon]

# 각 스케일에 대한 가우시안 가중 평균 곡률을 계산
multi_scale_curvatures = {scale: compute_gaussian_curvatures(bm, neighbor_verts_dict, curvatures, scale) for scale in scales}

# 각 스케일에 대한 살리언시 맵 생성 및 비선형 억제 적용
suppressed_saliency_maps = {scale: apply_non_linear_suppression(curvatures) for scale, curvatures in multi_scale_curvatures.items()}

# 최종 살리언시 맵 계산
final_saliency_map = [0] * len(bm.verts)
for saliency_map in suppressed_saliency_maps.values():
    final_saliency_map = [sum(x) for x in zip(final_saliency_map, saliency_map)]

# 최종 살리언시 맵 정규화
max_saliency = max(final_saliency_map)
final_saliency_map = [s / max_saliency for s in final_saliency_map]

# 정규화된 살리언시 값을 색상으로 매핑합니다.
colors = [map_saliency_to_color(s) for s in final_saliency_map]

# 메시의 각 정점에 색상을 적용합니다.
apply_vertex_colors(mesh, colors)

# bmesh를 해제합니다.
bm.free()

#--------------------------------------밑의 코드는 saliency를 매핑한 모델을 렌더링하는 코드---------------------------------------------


#카메라 세팅
camera_setting(camera, initial_location, initial_rotation)
#광원 세팅
light_setting(light, initial_location)

#렌더링 설정 (엔진 : BLENDER_EEVEE)
rendering_setting('BLENDER_EEVEE', resolution_x, resolution_y, samples)

# 다시 .obj로 불러온 객체를 선택
for obj in imported_objs:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    #새로운 재질 생성
    new_mat = set_material(obj)

    #saliency가 매핑된 재질
    configure_material_nodes(new_mat)



# 카메라 전방위 촬영
rendering('mesh_saliency', mesh_saliency_rendering_output_directory, file_name, rotateRadius, camera, light, initial_location)

#블렌더 종료
bpy.ops.wm.quit_blender()