import bpy
import math
import bmesh
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

# 색상 매핑 함수를 정의합니다.
def map_saliency_to_color(saliency):
    # 파란색에서 초록색으로
    if saliency < 0.35:
        r = 0
        g = saliency / 0.35
        b = 1
    # 초록색에서 노란색으로
    elif saliency < 0.64:
        r = (saliency - 0.35) / (0.64 - 0.35)
        g = 1
        b = 1 - r
    # 노란색에서 빨간색으로
    else:
        r = 1
        g = 1 - (saliency - 0.64) / (1.0 - 0.64)
        b = 0

    return (r, g, b, 1)  # RGBA 형식으로 반환

# 메시의 각 정점에 색상을 적용하는 함수
def apply_vertex_colors(mesh, colors):
    if not mesh.vertex_colors:
        mesh.vertex_colors.new()
    color_layer = mesh.vertex_colors.active.data

    for poly in mesh.polygons:
        for idx, loop_index in enumerate(poly.loop_indices):
            loop_vert_index = poly.vertices[idx]
            color_layer[loop_index].color = colors[loop_vert_index]

    mesh.update()
