import bpy
import bmesh

# Function to select edges based on a specific criterion
def select_specific_edges(mesh):
    edges_to_delete = []
    for edge in mesh.edges:
        # Example criterion: Select edges not part of any face
        if len(edge.link_faces) == 0:
            edges_to_delete.append(edge)
    return edges_to_delete


def remove_edges_not_include_face(obj):

    # Ensure you are in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Make sure the object is a mesh
    if obj.type == 'MESH':
        # Switch to edit mode and edge selection mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.tool_settings.mesh_select_mode = (False, True, False)  # (Vertices, Edges, Faces)

        # Get the mesh
        mesh = bmesh.from_edit_mesh(obj.data)

        # Deselect all first
        bpy.ops.mesh.select_all(action='DESELECT')
        mesh.select_flush(False)

        # Select specific edges
        edges_to_delete = select_specific_edges(mesh)

        # Delete selected edges
        if edges_to_delete:
            bmesh.ops.delete(mesh, geom=edges_to_delete, context='EDGES')

        # Update the mesh to reflect the changes
        bmesh.update_edit_mesh(obj.data)

        # Switch back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
    else:
        print("Selected object is not a mesh.")