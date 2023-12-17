import bpy


def make_manifold(obj):
    
    bpy.ops.preferences.addon_enable(module="object_print3d_utils")

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Switch to edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Reveal hidden mesh elements
    bpy.ops.mesh.reveal()

    # Select all elements
    bpy.ops.mesh.select_all(action='SELECT')

    # Delete loose parts
    bpy.ops.mesh.delete_loose(use_verts=True, use_edges=True, use_faces=True)

    # Deselect all elements
    bpy.ops.mesh.select_all(action='DESELECT')

    # Select and delete interior faces
    bpy.ops.mesh.select_interior_faces()
    bpy.ops.mesh.delete(type='FACE')

    # Select all elements again
    bpy.ops.mesh.select_all(action='SELECT')

    # Remove doubles (merge vertices close to each other)
    bpy.ops.mesh.remove_doubles(threshold=0.0001)

    # Select all elements again
    bpy.ops.mesh.select_all(action='SELECT')

    # Dissolve degenerate edges and faces
    bpy.ops.mesh.dissolve_degenerate(threshold=0.0001)

    # Select non-manifold edges and vertices
    bpy.ops.mesh.select_non_manifold(extend=False, use_wire=True, use_boundary=True, use_multi_face=False, use_non_contiguous=False, use_verts=True)

    # Select all elements again
    bpy.ops.mesh.select_all(action='SELECT')

    # Make normals consistent (recalculate outside)
    bpy.ops.mesh.normals_make_consistent()

    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Optional: clean non-manifold using 3D print toolbox (if available)
    bpy.ops.mesh.print3d_clean_non_manifold()