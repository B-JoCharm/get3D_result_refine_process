import os
import numpy as np
import math
import json


class Mesh:
    def __init__(self):
        self.vertices = []  # 정점 배열
        self.edges = set()  # 엣지 배열 (중복을 피하기 위해 집합 사용)
        self.faces = []     # 면 배열
        self.edge_face_map = {}

    def add_vertex(self, vertex):
        self.vertices.append(vertex)

    def add_face(self, face):
        self.faces.append(face)
        self._add_edges_from_face(face)

    def _add_edges_from_face(self, face):
        num_vertices = len(face)
        for i in range(num_vertices):
            # 순환적인 엣지를 위해 (i+1) % num_vertices 사용
            edge = (min(face[i], face[(i + 1) % num_vertices]), 
                    max(face[i], face[(i + 1) % num_vertices]))
            self.edges.add(edge)

    def calculate_edge_length(self, edge):
        vertex1 = self.vertices[edge[0]]
        vertex2 = self.vertices[edge[1]]
        return math.sqrt((vertex1[0] - vertex2[0])**2 + (vertex1[1] - vertex2[1])**2 + (vertex1[2] - vertex2[2])**2)

    def get_edge_lengths(self):
        return [self.calculate_edge_length(edge) for edge in self.edges]
    
    def calculate_triangle_area(self, face):
        # 삼각형의 각 변의 길이 계산
        edge_lengths = [
            self.calculate_edge_length((face[0], face[1])),
            self.calculate_edge_length((face[1], face[2])),
            self.calculate_edge_length((face[2], face[0]))
        ]

        # 헤론의 공식을 사용하여 면적 계산
        s = sum(edge_lengths) / 2  # 반둘레
        area = math.sqrt(s * (s - edge_lengths[0]) * (s - edge_lengths[1]) * (s - edge_lengths[2]))
        return area
        """
        area_value = s * (s - edge_lengths[0]) * (s - edge_lengths[1]) * (s - edge_lengths[2])

        # 음수 값 방지
        
        if area_value < 0:
            return 0  # 또는 다른 적절한 처리

        area = math.sqrt(area_value)
        return area
        """

    def get_face_areas(self):
        return [self.calculate_triangle_area(face) for face in self.faces]
    
    def calculate_vertex_degrees(self):
        vertex_degrees = [0] * len(self.vertices)
        for face in self.faces:
            for vertex in face:
                vertex_degrees[vertex] += 1
        return vertex_degrees
    
    def calculate_triangle_aspect_ratio(self, face):
        # 삼각형의 각 변의 길이 계산
        edge_lengths = [
            self.calculate_edge_length((face[0], face[1])),
            self.calculate_edge_length((face[1], face[2])),
            self.calculate_edge_length((face[2], face[0]))
        ]

        # 가장 긴 변과 가장 짧은 변 찾기
        longest_edge = max(edge_lengths)
        shortest_edge = min(edge_lengths)

        # 종횡비 계산
        if shortest_edge == 0:
            return float('inf')  # 0으로 나누기 방지
        return longest_edge / shortest_edge

    def get_face_aspect_ratios(self):
        # Calculate aspect ratios and filter out infinite values
        return [ratio for face in self.faces 
                if (ratio := self.calculate_triangle_aspect_ratio(face)) != float('inf')]
    

    def is_valid_vertex(self, vertex):
        return not (np.any(np.isnan(vertex)) or np.any(np.isinf(vertex)))

    def calculate_normal(self, face):
        vertices = [np.array(self.vertices[idx]) for idx in face]

        # Check if any vertex in the face is invalid
        if not all(self.is_valid_vertex(v) for v in vertices):
            return np.array([np.nan, np.nan, np.nan])

        v1, v2 = vertices[1] - vertices[0], vertices[2] - vertices[0]

        # Introduce a tolerance for degenerate faces
        tolerance = 1e-10  # This can be adjusted based on your data
        if np.linalg.norm(v1) < tolerance or np.linalg.norm(v2) < tolerance:
            return np.array([np.nan, np.nan, np.nan])

        normal = np.cross(v1, v2)

        # Further check for very small area
        if np.linalg.norm(normal) < tolerance:
            return np.array([np.nan, np.nan, np.nan])

        return normal

    def get_edge_dihedral_angles(self):
        # 각 엣지에 대한 면의 리스트를 저장
        edge_faces = {edge: [] for edge in self.edges}

        # 각 면에 대해, 엣지를 만들고 해당 엣지에 면을 할당
        for face in self.faces:
            num_vertices = len(face)
            for i in range(num_vertices):
                edge = (min(face[i], face[(i + 1) % num_vertices]), 
                        max(face[i], face[(i + 1) % num_vertices]))
                edge_faces[edge].append(face)

        # 이면각 계산
        edge_dihedral_angles = []
        for edge, faces in edge_faces.items():
            if len(faces) != 2:
                continue  # Skip edges that don't have exactly two adjacent faces

            normals = [self.calculate_normal(face) for face in faces]
            normal1, normal2 = normals[0], normals[1]

            # Check for degenerate faces (indicated by NaN in normals)
            if np.any(np.isnan(normal1)) or np.any(np.isnan(normal2)):
                continue  # Skip this edge as it involves a degenerate face

            # Calculate the dihedral angle
            cos_angle = np.dot(normal1, normal2) / (np.linalg.norm(normal1) * np.linalg.norm(normal2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Ensure the value is within the valid range for arccos
            angle = np.arccos(cos_angle)  # This is where 'angle' is defined

            edge_dihedral_angles.append(angle)  # Append the calculated angle

        return edge_dihedral_angles
    
    def find(self, parent, i):
        if parent[i] == i:
            return i
        return self.find(parent, parent[i])

    def union(self, parent, rank, x, y):
        xroot = self.find(parent, x)
        yroot = self.find(parent, y)

        if rank[xroot] < rank[yroot]:
            parent[xroot] = yroot
        elif rank[xroot] > rank[yroot]:
            parent[yroot] = xroot
        else:
            parent[yroot] = xroot
            rank[xroot] += 1

    def count_connected_components(self):
        parent = [i for i in range(len(self.vertices))]
        rank = [0] * len(self.vertices)

        for face in self.faces:
            for i in range(len(face)):
                x = self.find(parent, face[i])
                y = self.find(parent, face[(i + 1) % len(face)])
                self.union(parent, rank, x, y)

        # 연결된 컴포넌트의 수를 세어 반환
        return len(set([self.find(parent, i) for i in range(len(self.vertices))]))
    
    def calculate_bounding_box(self):
        if not self.vertices:
            return None

        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')

        for vertex in self.vertices:
            x, y, z = vertex
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            min_z = min(min_z, z)
            max_z = max(max_z, z)

        return [min_x, min_y, min_z], [max_x, max_y, max_z]
    
    # 고립된 정점 탐지
    def count_isolated_vertices(self):
        # 모든 정점을 면에 포함되지 않았다고 가정
        is_isolated = [True] * len(self.vertices)

        # 모든 면을 순회하면서 면에 포함된 정점을 표시
        for face in self.faces:
            for vertex in face:
                is_isolated[vertex] = False

        # 고립된 정점의 수를 반환
        return sum(is_isolated)
    
    # 중복 정점 갯수
    def count_duplicated_vertices(self):
        unique_vertices = set()
        duplicated_count = 0

        for vertex in self.vertices:
            if vertex in unique_vertices:
                duplicated_count += 1
            else:
                unique_vertices.add(vertex)

        return duplicated_count

    # 중복 면 갯수
    def count_duplicated_faces(self):
        unique_faces = set()
        duplicated_count = 0

        for face in self.faces:
            # 정점들을 정렬하여 순서에 상관없이 동일한 면을 비교할 수 있도록 함
            sorted_face = tuple(sorted(face))
            if sorted_face in unique_faces:
                duplicated_count += 1
            else:
                unique_faces.add(sorted_face)

        return duplicated_count
    
    # 경계 엣지 수
    def count_boundary_edges(self):
        # A dictionary to count the number of faces each edge belongs to
        edge_face_count = {}

        # Iterate over all faces and increment the count for each edge
        for face in self.faces:
            num_vertices = len(face)
            for i in range(num_vertices):
                edge = (min(face[i], face[(i + 1) % num_vertices]), 
                        max(face[i], face[(i + 1) % num_vertices]))
                if edge in edge_face_count:
                    edge_face_count[edge] += 1
                else:
                    edge_face_count[edge] = 1

        # Count edges that belong to only one face
        boundary_edges_count = sum(1 for edge in edge_face_count if edge_face_count[edge] == 1)

        return boundary_edges_count
    
    # 경계 루프 갯수
    def count_boundary_loops(self):
        boundary_edges = self._find_boundary_edges()
        visited_edges = set()
        loop_count = 0

        for edge in boundary_edges:
            if edge not in visited_edges:
                self._follow_boundary_loop(edge, boundary_edges, visited_edges)
                loop_count += 1

        return loop_count

    def _find_boundary_edges(self):
        edge_face_count = {}
        for face in self.faces:
            for i in range(len(face)):
                edge = (min(face[i], face[(i + 1) % len(face)]), max(face[i], face[(i + 1) % len(face)]))
                edge_face_count[edge] = edge_face_count.get(edge, 0) + 1

        return {edge for edge, count in edge_face_count.items() if count == 1}

    def _follow_boundary_loop(self, start_edge, boundary_edges, visited_edges):
        current_edge = start_edge
        visited_edges.add(current_edge)

        # Start vertex to check if we have completed the loop
        start_vertex = current_edge[0]
        current_vertex = current_edge[1]

        while True:
            # Find the next boundary edge that shares the current vertex and is not already visited
            next_edges = [edge for edge in boundary_edges if edge not in visited_edges and current_vertex in edge]

            if not next_edges:
                # No more connected edges, end of loop
                break

            next_edge = next_edges[0]
            visited_edges.add(next_edge)
            current_edge = next_edge

            # Update the current vertex
            current_vertex = next_edge[0] if next_edge[0] != current_vertex else next_edge[1]

            # Check if the loop is closed
            if current_vertex == start_vertex:
                break

    # 면적이 0인 면의 수
    def count_degenerated_faces(self):
        degenerated_count = 0
        for face in self.faces:
            if self._is_degenerated_face(face):
                degenerated_count += 1
        return degenerated_count

    def _is_degenerated_face(self, face):
        # A triangle is degenerated if its area is close to zero
        return self.calculate_triangle_area(face) < 1e-15
    
    def is_oriented(self):
        # 각 면의 법선 계산
        face_normals = {i: self.calculate_normal(face) for i, face in enumerate(self.faces)}

        # 각 면에 대해 인접한 면들과의 법선 방향 일치 여부 검사
        for i, face in enumerate(self.faces):
            current_normal = face_normals[i]

            # 인접 면 찾기
            adjacent_faces = self._find_adjacent_faces(i)

            for adjacent_face in adjacent_faces:
                adjacent_normal = face_normals[adjacent_face]

                # 내적이 음수라면, 두 법선이 반대 방향임
                if np.dot(current_normal, adjacent_normal) < 0:
                    return False

        return True

    def _find_adjacent_faces(self, face_index):
        adjacent_faces = set()
        face = self.faces[face_index]
        num_vertices = len(face)

        for i in range(num_vertices):
            edge = (min(face[i], face[(i + 1) % num_vertices]), 
                    max(face[i], face[(i + 1) % num_vertices]))
            if edge in self.edge_face_map:
                for adjacent_face_index in self.edge_face_map[edge]:
                    if adjacent_face_index != face_index:
                        adjacent_faces.add(adjacent_face_index)

        return list(adjacent_faces)  
    
    # 닫힌 메쉬인지 판단
    def is_closed(self):
        edge_face_count = {}
        
        # Count the number of faces each edge belongs to
        for face in self.faces:
            num_vertices = len(face)
            for i in range(num_vertices):
                edge = (min(face[i], face[(i + 1) % num_vertices]), 
                        max(face[i], face[(i + 1) % num_vertices]))
                edge_face_count[edge] = edge_face_count.get(edge, 0) + 1

        # Check if all edges belong to exactly two faces
        for edge_count in edge_face_count.values():
            if edge_count != 2:
                return False  # Found a boundary edge or an edge shared by more than 2 faces

        return True  # No boundary edges found, the mesh is closed
    
    # 엣지 매니폴드 판단
    def is_edge_manifold(self):
        edge_face_count = {}

        # Count the number of faces each edge belongs to
        for face in self.faces:
            num_vertices = len(face)
            for i in range(num_vertices):
                edge = (min(face[i], face[(i + 1) % num_vertices]), 
                        max(face[i], face[(i + 1) % num_vertices]))
                edge_face_count[edge] = edge_face_count.get(edge, 0) + 1

        # Check if any edge belongs to more than two faces
        for count in edge_face_count.values():
            if count > 2:
                return False  # Found an edge that is not manifold

        return True  # All edges are manifold
    
    def is_vertex_manifold(self):
        # Create a map from vertices to their adjacent faces and edges
        vertex_face_map = {v: set() for v in range(len(self.vertices))}
        vertex_edge_map = {v: set() for v in range(len(self.vertices))}
        for i, face in enumerate(self.faces):
            for j, vertex in enumerate(face):
                vertex_face_map[vertex].add(i)
                edge = (min(vertex, face[(j + 1) % len(face)]), max(vertex, face[(j + 1) % len(face)]))
                vertex_edge_map[vertex].add(edge)

        # Check each vertex
        for vertex, faces in vertex_face_map.items():
            if not self._is_vertex_manifold(vertex, faces, vertex_edge_map[vertex]):
                return False  # Found a vertex that violates the manifold condition

        return True  # All vertices are manifold

    def _is_vertex_manifold(self, vertex, faces, edges):
        # In a manifold, the number of edges should be equal to or one more than the number of faces
        # The extra edge is for the boundary loop case
        return len(edges) == len(faces) or len(edges) == len(faces) + 1

    def load_obj(self, filename):
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    parts = line.split()
                    vertex = tuple(map(float, parts[1:4]))  # x, y, z 좌표
                    self.add_vertex(vertex)
                elif line.startswith('f '):
                    parts = line.split()
                    # OBJ 파일은 1부터 인덱싱하지만 Python은 0부터 인덱싱함을 고려
                    face = [int(p.split('/')[0]) - 1 for p in parts[1:]]
                    self.add_face(face)


# 분산 계산
def calculate_variance(data):
    if len(data) < 2:
        raise ValueError("Variance requires at least two data points")

    mean = sum(data) / len(data)
    squared_diff = [(x - mean) ** 2 for x in data]
    variance = sum(squared_diff) / (len(data) - 1)  # For a sample; use len(data) for a population
    return variance


# 백분위수 구한후 저장
def quantile_breakdown(data, name, info, txt_path, with_total=False):

    ave = np.mean(data)
    var = calculate_variance(data)

    if with_total:
        total = np.sum(data)

    p0, p25, p50, p75, p90, p95, p100 =\
            np.percentile(data, [0, 25, 50, 75, 90, 95, 100])

    text = "-- {} --\n".format(name)
    text += "min: {:^7.3}\n".format(p0)
    text += "25%: {:^7.3}\n".format(p25)
    text += "50%: {:^7.3}\n".format(p50)
    text += "75%: {:^7.3}\n".format(p75)
    text += "90%: {:^7.3}\n".format(p90)
    text += "95%: {:^7.3}\n".format(p95)
    text += "max: {:^7.3}\n".format(p100)
    text += "ave: {:.6g}\n".format(ave)
    text += "var: {:.6g}\n".format(var)
    if with_total:
        text += "total: {:.6g}\n".format(total)
  
    info["ave_{}".format(name)] = ave
    info["var_{}".format(name)] = var
    info["max_{}".format(name)] = p100
    info["min_{}".format(name)] = p0
    info["p25_{}".format(name)] = p25
    info["median_{}".format(name)] = p50
    info["p75_{}".format(name)] = p75
    info["p90_{}".format(name)] = p90
    info["p95_{}".format(name)] = p95
    info["max_{}".format(name)] = p100
    if with_total:
        info["total_{}".format(name)] = total
    
    if txt_path:
        append_to_file(txt_path, text)

    

# 기본 정보 저장
def save_basic_info(mesh ,info ,txt_path):

    num_vertex = len(mesh.vertices)
    num_face = len(mesh.faces)
    num_edge = len(mesh.edges)
    
    # 각 면에 속한 정점의 수를 합산
    total_vertices_in_faces = sum(len(face) for face in mesh.faces)

    # 면의 수
    num_faces = len(mesh.faces)

    # 면 당 평균 정점 수 계산
    average_vertices_per_face = total_vertices_in_faces / num_faces

    text = "-- Basic information --\n"
    text += f"Vertex count: {num_vertex}\n"
    text += f"Edge count: {num_edge}\n"
    text += f"Face count: {num_face}\n"
    text += f"vertex per face: {average_vertices_per_face}\n"

    info["num_vertex"] = num_vertex
    info["num_edge"] = num_edge
    info["num_face"] = num_face
    info["vertices_per_face"] = average_vertices_per_face

    if txt_path:
        append_to_file(txt_path, text)

# 바운딩 박스 저장
def save_bounding_box(mesh ,info ,txt_path):

    box_min, box_max = mesh.calculate_bounding_box()

    box_size = [round(box_max[0]-box_min[0], 6), round(box_max[1]-box_min[1], 6), round(box_max[2]-box_min[2], 6)]

    text = "-- Boundding box --\n"
    text += f"bbox_min: {box_min}\n"
    text += f"bbox_max: {box_max}\n" 
    text += f"bbox_size: {box_size}\n"  

    if txt_path:
        append_to_file(txt_path, text)

# Edge Length ( 엣지 길이 )
def save_edge_length(mesh, info, txt_path):

    edge_lengths = mesh.get_edge_lengths()
    data = edge_lengths
    quantile_breakdown(data, "Edge Length", info , txt_path)

# Area Size ( 면적 크기 ) 
def save_area_size(mesh, info, txt_path):

    face_areas = mesh.get_face_areas()
    data = face_areas
    quantile_breakdown(data, "Area Size", info , txt_path, True)

# Vertex Valance ( 정점 차수 )  
def save_vertex_valance(mesh, info, txt_path):

    vertex_degrees = mesh.calculate_vertex_degrees()
    data = vertex_degrees
    quantile_breakdown(data, "Vertex Valance", info , txt_path)

# Face Aspect Ratio ( 면 종횡비 )       계산값 정확성 애매함
def save_face_acpect(mesh, info, txt_path):

    face_aspect_ratios = mesh.get_face_aspect_ratios()
    data = face_aspect_ratios
    quantile_breakdown(data, "Face Aspect Ratio", info , txt_path)

# Edge Dihedral Angle ( 모서리 이면각 )       
def save_dihedral_angle(mesh, info, txt_path):

    edge_dihedral_angles = mesh.get_edge_dihedral_angles()
    # 라디안 각을 도 표기법으로 바꿈
    # data = list(map(math.degrees, edge_dihedral_angles))
    data = edge_dihedral_angles
    quantile_breakdown(data, "Edge Dihedral Angle", info , txt_path)

# 그 외 정보
def save_extended_info(mesh, info, txt_path):

    num_vertex = len(mesh.vertices)
    num_face = len(mesh.faces)
    num_edge = len(mesh.edges)

    # 오일러 특성
    eluer_charater = num_vertex - num_edge + num_face

    # 연결 요소 수
    num_connected_components = mesh.count_connected_components()

    # 고립된 정점 수
    num_isolated_vertices = mesh.count_isolated_vertices()

    # 중복된 정점 수
    num_duplicated_vertices = mesh.count_duplicated_vertices()

    # 중복된 면 수
    num_duplicated_faces = mesh.count_duplicated_faces()

    # 경계 엣지 수
    num_boundary_edges = mesh.count_boundary_edges()

    # 경계 모서리 수
    num_boundary_loops = mesh.count_boundary_loops()

    # 영역의 크기가 0이되는 면 갯수
    num_degenerated_faces = mesh.count_degenerated_faces()

    # 엣지 매니폴드 판단
    edge_manifold = mesh.is_edge_manifold()

    # 정점 매니폴드 판단
    vertex_manifold = mesh.is_vertex_manifold()

    # 일관된 방향 판단
    oriented = mesh.is_oriented()

    # 닫힌 메쉬 판단
    # closed = mesh.is_watertight

    text = "-- Extended info --\n"
    text += f"euler characteristic : {eluer_charater}\n"
    text += f"num connected components : {num_connected_components}\n"
    text += f"num isolated vertices : {num_isolated_vertices}\n"
    text += f"num duplicated vertices : {num_duplicated_vertices}\n"
    text += f"num duplicated faces : {num_duplicated_faces}\n"
    text += f"num boundary edges : {num_boundary_edges}\n"
    text += f"num boundary loops : {num_boundary_loops}\n"
    text += f"num degenerated faces : {num_degenerated_faces}\n"
    text += f"edge manifold : {edge_manifold}\n"
    text += f"vertex manifold : {vertex_manifold}\n"
    text += f"oriented : {oriented}\n"


    info["euler characteristic"] = eluer_charater
    info["num connected components"] = num_connected_components
    info["num isolated vertices"] = num_isolated_vertices
    info["num duplicated vertices"] = num_duplicated_vertices
    info["num duplicated faces"] = num_duplicated_faces
    info["num boundary edges"] = num_boundary_edges
    info["num boundary loops"] = num_boundary_loops
    info["num degenerated faces"] = num_degenerated_faces
    info["edge manifold"] = edge_manifold
    info["vertex manifold"] = vertex_manifold
    info["oriented"] = oriented
  

    if txt_path:
        append_to_file(txt_path, text)    



# 데이터를 파일에 추가하는 함수
def append_to_file(path, text):
    with open(path, 'a') as file:  # 'a' 모드는 파일에 데이터를 추가합니다
        file.write(text + '\n')  # 데이터 끝에 개행 문자를 추가하여 줄바꿈을 합니다



# 메쉬 정보를 txt로 저장
def save_status(obj_path, save_path, save_txt = True , save_data = False):

    txt_path = os.path.join(save_path, "meshstatus.txt")

    if save_txt:
        if os.path.exists(txt_path):
            os.remove(txt_path)
    else:
        txt_path = None
    

    mesh = Mesh()
    mesh.load_obj(obj_path)

    # info 딕셔너리
    info = {}

    save_basic_info(mesh ,info ,txt_path)
    save_bounding_box(mesh ,info ,txt_path)
    save_edge_length(mesh, info, txt_path)
    save_area_size(mesh, info, txt_path)
    save_vertex_valance(mesh, info, txt_path)
    save_face_acpect(mesh, info, txt_path)
    save_dihedral_angle(mesh, info, txt_path)
    save_extended_info(mesh, info, txt_path)


    if save_data:
        # Extracting the file name
        file_name_with_extension = os.path.basename(obj_path)

        # Splitting the file name and extension
        file_name, file_extension = os.path.splitext(file_name_with_extension)

        file_path = os.path.join(save_path, 'data_{}.json'.format(file_name))

        with open(file_path, 'w') as file:
            json.dump(info, file)

    return info


    

if __name__ == "__main__":

    crrent_path = os.path.dirname(os.path.realpath(__file__))
    obj_path = os.path.join(crrent_path, "0000009.obj")

    save_status(obj_path, crrent_path, True)