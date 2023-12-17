import bpy
import bmesh

def find_boundary_loops(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    visited_edges = set()  # Track visited edges
    boundary_loops = []

    for edge in bm.edges:
        if edge.is_boundary and edge not in visited_edges:
            loop = []
            current_edge = edge
            start_vert = edge.verts[0]
            loop.append(start_vert.index)

            while current_edge:
                # Add current edge to visited and current vertex to the loop
                visited_edges.add(current_edge)
                next_vert = current_edge.other_vert(start_vert)

                if next_vert in loop:
                    # Loop closure detected
                    break

                loop.append(next_vert.index)

                # Find the next boundary edge
                next_edge = None
                for e in next_vert.link_edges:
                    if e.is_boundary and e not in visited_edges:
                        next_edge = e
                        break

                start_vert = next_vert
                current_edge = next_edge

            boundary_loops.append(loop)

    bm.free()
    return boundary_loops

def create_vertex_groups(obj, boundary_loops):
    obj.vertex_groups.clear()  # Clear existing groups
    for i, loop in enumerate(boundary_loops):
        group = obj.vertex_groups.new(name=f'BoundaryLoop_{i}')
        for vertex_index in loop:
            group.add([vertex_index], 1.0, 'ADD')

def extract_edge_indices(edge_list):
    # Extract edge indices directly from BMEdge objects
    return [edge.index for edge in edge_list]

def do_edges_form_face(obj, edge_indices):
    # Ensure the object is a mesh
    if obj.type != 'MESH':
        return False

    # Get mesh data
    mesh = obj.data

    # Collect vertices of the edges
    edge_vertices = set()
    for edge_index in edge_indices:
        edge = mesh.edges[edge_index]
        edge_vertices.update(edge.vertices)

    # Check if any face contains all these vertices
    for face in mesh.polygons:
        if edge_vertices.issubset(face.vertices):
            return True

    return False

def create_faces_for_vertex_groups(obj, boundary_loops):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()

    for loop in boundary_loops:
        bm.verts.ensure_lookup_table()  # Ensure the lookup table is updated
        bm.edges.ensure_lookup_table()  # Do the same for edges if necessary

        if len(loop) >= 3:
            # Create a list of edges for the loop
            edges = []
            for i in range(len(loop)):
                v1 = bm.verts[loop[i]]
                v2 = bm.verts[loop[(i + 1) % len(loop)]]

                # Check if vertices are different
                if v1 != v2:
                    edge = bm.edges.get([v1, v2]) or bm.edges.new([v1, v2])
                    edges.append(edge)

            if edges:
                edge_indices = extract_edge_indices(edges)
                is_face = do_edges_form_face(obj, edge_indices)
                if is_face:
                    face_to_remove = None
                    for face in bm.faces:
                        if all(edge in face.edges for edge in edges):
                            face_to_remove = face
                            break
                    
                    if face_to_remove:
                        bmesh.ops.delete(bm, geom=[face_to_remove], context='FACES_ONLY')                    
                else:
                    try:
                        bmesh.ops.edgeloop_fill(bm, edges=edges, mat_nr=0, use_smooth=False)
                    except ValueError as e:
                        print(f"Error filling loop: {e}")

        elif len(loop) == 2:
            # Merge two vertices
            v1, v2 = [bm.verts[i] for i in loop]
            if v1 != v2:
                bmesh.ops.pointmerge(bm, verts=[v1, v2], merge_co=v1.co)
                
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()

    bm.to_mesh(obj.data)
    bm.free()

def remove_boundary_loops(obj):

    # Ensure we have an active object and it's a mesh
    bpy.ops.object.mode_set(mode='OBJECT')

    active_obj = bpy.context.active_object
    if active_obj and active_obj.type == 'MESH':
        boundary_loops = find_boundary_loops(active_obj)
        create_vertex_groups(active_obj, boundary_loops)
        create_faces_for_vertex_groups(active_obj, boundary_loops)