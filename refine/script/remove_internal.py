import bpy
import bmesh
import math
from mathutils import bvhtree
from mathutils import Matrix
from mathutils import Vector

def select_visible_vertices(obj, initial_location, rotateRadius):
    bpy.context.view_layer.update()
    bpy.ops.object.mode_set(mode='OBJECT')

    # Create a BVH tree and BMesh
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bvh = bvhtree.BVHTree.FromBMesh(bm)
    
    if obj and obj.type == 'MESH':
        for i in range(0,360,rotateRadius):
            for j in range(0,360,rotateRadius):
                
                y_rotation_matrix = Matrix.Rotation(math.radians(j), 4, 'Y')
                
                z_rotation_matrix = Matrix.Rotation(math.radians(i), 4, 'Z')
                        
                initial_location_vec = Vector(initial_location)
                
                new_location_vec = z_rotation_matrix @ y_rotation_matrix @ initial_location_vec
                    
                for v in bm.verts:
                    
                    if mesh.vertices[v.index].select is True:
                        continue
                    
                    # Calculate the direction from the camera to the vertex
                    direction = (v.co - new_location_vec).normalized()

                    # Perform a ray cast from the camera to the vertex
                    hit, _, _, _ = bvh.ray_cast(new_location_vec, direction, 10000)

                    if hit is not None:
                        # If the ray hit is very close to the vertex, select the vertex
                        if (hit - v.co).length < 0.001:
                            mesh.vertices[v.index].select = True

    bm.free()
    
    
def delete_unselected_vertices(obj):
    # Ensure the object is a mesh
    if obj.type != 'MESH':
        raise TypeError("Object must be a mesh")

    # Switch to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Create a BMesh from the object
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    # Collect unselected vertices
    unselected_verts = [v for v in bm.verts if not v.select]

    # Delete unselected vertices
    bmesh.ops.delete(bm, geom=unselected_verts, context='VERTS')

    # Update the mesh with the new BMesh data
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')


# 내부 정점 제거
def remove_internal_vertices(obj, angle = 10, initial_location = (10, 0, 0)):

    select_visible_vertices(obj, initial_location, angle)

    delete_unselected_vertices(obj)