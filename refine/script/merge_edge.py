import bpy
import bmesh
import numpy as np
from mathutils import Vector

def calculate_mean_edge(obj):

    bm = bmesh.new()
    bm.from_mesh(obj.data)

    edge_lengths = [edge.calc_length() for edge in bm.edges]
    average_length = np.mean(edge_lengths)

    bm.free()

    return average_length


def merge_edge(obj, gamma = 0.2):

    bpy.ops.object.mode_set(mode='EDIT')

    average_length = calculate_mean_edge(obj)

    length_threshold = average_length * gamma

    bpy.ops.mesh.remove_doubles(threshold=length_threshold)

    bpy.ops.object.mode_set(mode='OBJECT')





