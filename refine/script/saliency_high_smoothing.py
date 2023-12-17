import bpy
import math
import bmesh
import numpy as np
from mathutils import Vector


# 이웃 정점 구하는 함수
def find_neighbors(bm):
    neighbor_verts_dict = {}
    for v in bm.verts:
        # 해당 정점에 연결된 이웃 정점을 찾고
        neighbors = [edge.other_vert(v) for edge in v.link_edges]
        # 이웃 정점의 인덱스를 저장
        neighbor_verts_dict[v.index] = [v_neighbor.index for v_neighbor in neighbors]
    return neighbor_verts_dict

# 모든 정점에서의 곡률 구하는 함수
def find_curvature(bm):
    curvatures = []
    for v in bm.verts:
        angle_sum = 0
        for f in v.link_faces:
            if v.normal.length > 0 and f.normal.length > 0:
                angle_sum += math.degrees(v.normal.angle(f.normal))

        if v.link_faces:
            avg_angle = angle_sum / len(v.link_faces)
        else:
            avg_angle = 0

        curvatures.append(avg_angle)
    return curvatures

# 모델의 경계 상자 대각선 길이를 계산하는 함수
def calculate_diagonal_length(obj):
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return (bbox_corners[6] - bbox_corners[0]).length

# 가우시안 가중 평균 곡률을 계산하는 함수
def compute_gaussian_curvatures(bm, neighbor_verts_dict, curvatures, sigma):
    bm.verts.ensure_lookup_table() #bm.verts의 인덱스를 사용하기전에 bmesh의 내부 인텍스 테이블이 최신 상태임을 보장하여 IndexError가 발생하지 않도록 해줌
    gaussian_curvatures = []
    for v in bm.verts:
        weight_sum = 0
        weighted_curvature_sum = 0
        for neighbor_index in neighbor_verts_dict[v.index]:
            # 이웃 정점과의 거리를 계산합니다.
            distance = (v.co - bm.verts[neighbor_index].co).length
            # 가우시안 가중치를 계산합니다.
            weight = math.exp(-(distance ** 2) / (2 * (sigma ** 2)))
            # 가중치와 이웃 정점의 곡률을 곱합니다.
            weighted_curvature_sum += weight * curvatures[neighbor_index]
            weight_sum += weight
        
        # 가우시안 가중 평균 곡률을 계산합니다.
        gaussian_curvature = weighted_curvature_sum / weight_sum if weight_sum != 0 else 0
        gaussian_curvatures.append(gaussian_curvature)
    return gaussian_curvatures

# 살리언시 맵을 정규화하고 비선형 억제를 적용하는 함수
def apply_non_linear_suppression(curvatures):
    max_curvature = max(curvatures)
    local_maxima = [c for c in curvatures if c != max_curvature]
    avg_local_max = sum(local_maxima) / len(local_maxima) if local_maxima else 0
    suppression_factor = (max_curvature - avg_local_max) ** 2
    return [c * suppression_factor for c in curvatures]

def saliency_based_smoothing(obj, saliency_threshold = 0.25, smoothingIteration = 30,lambda_factor = 0.1):
    mesh = obj.data

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    neighbor_verts_dict = find_neighbors(bm)
    curvatures = find_curvature(bm)
    diagonal_length = calculate_diagonal_length(obj)
    epsilon = 0.003 * diagonal_length
    scales = [2 * epsilon, 3 * epsilon, 4 * epsilon, 5 * epsilon, 6 * epsilon]

    multi_scale_curvatures = {scale: compute_gaussian_curvatures(bm, neighbor_verts_dict, curvatures, scale) for scale in scales}
    suppressed_saliency_maps = {scale: apply_non_linear_suppression(curvatures) for scale, curvatures in multi_scale_curvatures.items()}

    final_saliency_map = [0] * len(bm.verts)
    for saliency_map in suppressed_saliency_maps.values():
        final_saliency_map = [sum(x) for x in zip(final_saliency_map, saliency_map)]

    max_saliency = max(final_saliency_map)
    final_saliency_map = [s / max_saliency for s in final_saliency_map]
    
    bpy.ops.object.mode_set(mode='OBJECT')

    high_saliency_verts = [vert for vert, saliency in zip(bm.verts, final_saliency_map) if saliency <= saliency_threshold]

    obj.vertex_groups.new(name='High Saliency Vertices')
    vertex_group = obj.vertex_groups['High Saliency Vertices']
    for v in high_saliency_verts:
        vertex_group.add([v.index], 1.0, 'ADD')

    mod = obj.modifiers.new(name="LaplacianSmooth", type='LAPLACIANSMOOTH')
    mod.vertex_group = vertex_group.name
    mod.iterations = smoothingIteration  # 반복 횟수 설정
    mod.lambda_factor = lambda_factor  # 스무딩 강도 설정 (0에서 1 사이의 값)
    mod.use_volume_preserve = False
    
    bpy.ops.object.modifier_apply({"object": obj}, modifier=mod.name)


    bm.free()