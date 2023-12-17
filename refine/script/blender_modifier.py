import bpy

def apply_modifier(obj, modifier_name):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier_name)


def mirror_modifier(obj):

    # Ensure we are in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add Mirror Modifier
    modifier_name = "Mirror"
    mirror_modifier = obj.modifiers.new(name=modifier_name, type='MIRROR')

    # Set Clipping
    mirror_modifier.use_clip = True

    # Set the mirror axis, for example, mirroring on the X-axis
    mirror_modifier.use_axis[0] = False   # X
    mirror_modifier.use_axis[1] = False   # Y
    mirror_modifier.use_axis[2] = True    # Z

    # Enable Bisect
    mirror_modifier.use_bisect_axis[0] = False  # Bisect on X
    mirror_modifier.use_bisect_axis[1] = False  # bisect on Y
    mirror_modifier.use_bisect_axis[2] = True   # bisect on Z

    # Merge vertices (optional)
    mirror_modifier.use_mirror_merge = True
    mirror_modifier.merge_threshold = 0.001  # Adjust as necessary
        
    # Apply the Mirror Modifier
    apply_modifier(obj, modifier_name)


def remesh_modifier(obj, octree_depth = 6, scale = 0.9):
    # Ensure we are in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add Remesh Modifier
    remesh_modifier = obj.modifiers.new(name="Remesh", type='REMESH')

    # Set Remesh Modifier properties
    remesh_modifier.mode = 'SMOOTH'                  # Set mode to Smooth
    remesh_modifier.octree_depth = octree_depth      # Set octree depth (adjust as needed)
    remesh_modifier.scale = scale                    # Set scale (adjust as needed)
    remesh_modifier.use_remove_disconnected = False  # Disable remove disconnected

    # Apply the Remesh Modifier
    apply_modifier(obj, remesh_modifier.name)


def triangulate_modifier(obj):
    # Ensure we are in object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    # Add Triangulate Modifier
    triangulate_modifier = obj.modifiers.new(name="Triangulate", type='TRIANGULATE')

    # Apply the Triangulate Modifier
    apply_modifier(obj, triangulate_modifier.name)


def laplacian_smoothing_modifier(obj, iterations=3, lambda_factor=0.1):

    bpy.ops.object.mode_set(mode='OBJECT')

    laplacian_smoothing_modifier = obj.modifiers.new(name="LaplacianSmooth", type='LAPLACIANSMOOTH')

    laplacian_smoothing_modifier.iterations = iterations
    laplacian_smoothing_modifier.lambda_factor = lambda_factor
    laplacian_smoothing_modifier.use_volume_preserve = False

    apply_modifier(obj, laplacian_smoothing_modifier.name)

def decimate_modifier(obj, ratio = 0.5):

    bpy.ops.object.mode_set(mode='OBJECT')

    decimate_modifier = obj.modifiers.new(name="Decimate", type='DECIMATE')


    decimate_modifier.decimate_type = 'COLLAPSE'
    decimate_modifier.ratio = ratio
    decimate_modifier.use_symmetry = True
    decimate_modifier.symmetry_axis = 'Z'

    apply_modifier(obj, decimate_modifier.name)