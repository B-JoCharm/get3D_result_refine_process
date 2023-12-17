import bpy
import bmesh
from collections import defaultdict

def get_connected_verts(bm, start_vert):
    """연결된 정점들을 찾는 함수"""
    seen = set([start_vert])
    queue = [start_vert]
    while queue:
        v = queue.pop()
        seen.add(v)
        linked = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) not in seen]
        queue.extend(linked)
    return seen


def remove_connected_components(obj, gamma=0.2, min_component = 6):

    # 활성 메쉬 가져오기
    mesh = obj.data

    # 메쉬에서 bmesh 생성
    bm = bmesh.new()
    bm.from_mesh(mesh)

    # 연결 요소 찾기
    visited = set()
    connected_components = []
    for v in bm.verts:
        if v not in visited:
            verts = get_connected_verts(bm, v)
            visited.update(verts)
            connected_components.append(verts)

    # 연결 요소 정렬
    connected_components.sort(key=len, reverse=True)

    # 연결 요소 수
    num_connected_components = len(connected_components)

    # 유지할 연결 요소 개수 설정
    keep_count = int(num_connected_components * gamma)  # 유지할 연결 요소 개수

    if keep_count <= min_component:
        keep_count = min_component

    # 나머지 연결 요소 제거
    for comp in connected_components[keep_count:]:
        bm.verts.ensure_lookup_table()  # 이 부분을 추가
        bmesh.ops.delete(bm, geom=[bm.verts[i.index] for i in comp], context='VERTS')

    # bmesh를 다시 메쉬에 쓰기
    bm.to_mesh(mesh)
    bm.free()

    # 메쉬 업데이트
    mesh.update()
