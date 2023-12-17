import bpy

def dissolve_manifold_vertex(obj):

    bpy.context.view_layer.objects.active = obj

    # Switch to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Deselect all vertices
    bpy.ops.mesh.select_all(action='DESELECT')

    # Select non-manifold vertices
    bpy.ops.mesh.select_non_manifold()

    # Dissolve the selected vertices
    bpy.ops.mesh.dissolve_verts()

    # Return to object mode
    bpy.ops.object.mode_set(mode='OBJECT')