import bpy
import math
import mathutils
import os
import sys
import bmesh
from mathutils import Vector
from math import degrees

def camera_setting(camera, location, rotation):
    if camera:
        # 카메라 이동
        camera.location = location 

        # 카메라 회전 (라디안 단위로 회전값을 설정)
        camera.rotation_euler = rotation

        # 변경 사항 적용
        bpy.context.view_layer.update()
    else:
        print("카메라를 찾을 수 없습니다. 이름을 확인하십시오.")

def light_setting(light, location):
    if light:
        # 광원의 위치를 변경합니다.
        light.location = location  

        # 변경된 위치를 적용합니다.
        bpy.context.view_layer.update()

    else:
        print("광원을 찾을 수 없습니다. 이름을 확인하십시오.")

#메시 불러오기 및 초기설정(불러온 객체 선택 및 활성화, 스케일조정), imported_objs로 선택된 객체 리스트를 반환함에 따라 불러온 객체를 다시 선택할때 사용 가능
def mesh_initial_setting(obj_file, texture_file):
    # 모든 객체 선택 해제
    bpy.ops.object.select_all(action='DESELECT')

    # .obj 파일 불러오기 전의 객체 목록
    before_import = set(bpy.context.scene.objects)

    # .obj 파일 불러오기
    bpy.ops.import_scene.obj(filepath=obj_file, filter_glob="*.obj;*.mtl", axis_forward='-Z', axis_up='Y')

    # .obj 파일로 불러온 객체들의 참조를 저장
    imported_objs = [o for o in bpy.context.scene.objects if o not in before_import]
    
    # 가져온 모델 선택 (텍스쳐가 없다면 재질 활성화까지)
    if os.path.exists(texture_file):
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
    else:
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
            
                # .mtl 파일에서 가져온 재질을 활성화합니다.
                if obj.data.materials:
                    for mat in obj.data.materials:
                        obj.active_material = mat
            
    # 스케일 조정 (X, Y, Z 축의 스케일을 5로 설정), 하나의 메시만 불러오므로 이렇게 사용 가능 (여러 메시를 불러올 경우 imported_objs리스트를 돌면서 각 객체에 대해 적용해야함)
    bpy.context.object.scale[0] = 5
    bpy.context.object.scale[1] = 5
    bpy.context.object.scale[2] = 5

    return imported_objs

#재질 및 텍스처 적용 (텍스처 파일이 있는 경우에만 사용 가능)
def apply_mtl_and_texture(texture_file):
    bpy.ops.object.material_slot_remove()
    bpy.ops.object.material_slot_add()
    bpy.data.materials[0].name = 'Material'
    bpy.context.object.data.materials[0] = bpy.data.materials['Material']
    bpy.data.materials['Material'].use_nodes = True
    bsdf = bpy.data.materials['Material'].node_tree.nodes["Principled BSDF"]
    texture = bpy.data.materials['Material'].node_tree.nodes.new('ShaderNodeTexImage')
    texture.location = (-200, 300)
    texture.image = bpy.data.images.load(texture_file)
    bpy.data.materials['Material'].node_tree.links.new(bsdf.inputs['Base Color'], texture.outputs['Color'])

#렌더링 설정(cycle, eveee)
def rendering_setting(engine, resolution_x, resolution_y, samples):
    if engine == 'CYCLES':
        # Cycles 렌더 엔진 설정
        bpy.context.scene.render.engine = 'CYCLES'

        # 해상도 및 샘플링 설정
        bpy.context.scene.render.resolution_x = resolution_x
        bpy.context.scene.render.resolution_y = resolution_y
        bpy.context.scene.cycles.samples = samples
    else:
        # 사용하려는 렌더링 엔진을 설정 (예: Eevee)
        bpy.context.scene.render.engine = 'BLENDER_EEVEE' 

        # 해상도 설정
        bpy.context.scene.render.resolution_x = resolution_x
        bpy.context.scene.render.resolution_y = resolution_y

        # BLENDER_EEVEE 엔진에 대한 샘플링 설정 (안써도 되는것 같긴함)
        bpy.context.scene.eevee.taa_render_samples = samples

# 카메라 전방위 촬영
def rendering(type,output_directory, file_name, rotateRadius, camera, light, initial_location):
    
    for i in range(0,360,rotateRadius):
        for j in range(0,360,rotateRadius):
            
            y_rotation_matrix = mathutils.Matrix.Rotation(math.radians(j), 4, 'Y')
            
            z_rotation_matrix = mathutils.Matrix.Rotation(math.radians(i), 4, 'Z')
                    
            initial_location_vec = mathutils.Vector(initial_location)

            camera.location = z_rotation_matrix @ y_rotation_matrix @ initial_location_vec
            
            light.location = z_rotation_matrix @ y_rotation_matrix @ initial_location_vec

            camera.rotation_euler = (math.radians(90+j), 0, math.radians(90+i))
        
            bpy.context.view_layer.update()
            
            # 각도를 기반으로 렌더링 출력 파일 이름 설정
            if type == 'mesh':
                output_file = os.path.join(output_directory, f"{file_name}_render_z{i}_y{j}.png")
            else:
                output_file = os.path.join(output_directory, f"{file_name}_render_mesh_saliency_z{i}_y{j}.png")

            # 이미지 렌더링
            bpy.context.scene.render.filepath = output_file
            bpy.ops.render.render(write_still=True)

#saliency가 매핑된 오브젝트를 렌더링 하기위해 Diffuse_Material 생성
def set_material(obj, material_name="Diffuse_Material"):
    # 오브젝트에 재질이 없다면 새로운 재질을 추가
    if not obj.data.materials:
        new_mat = bpy.data.materials.new(name=material_name)
        obj.data.materials.append(new_mat)
    else:
        new_mat = obj.data.materials[0]

    return new_mat

#saliency가 매핑된 오브젝트를 렌더링 하기위해 메테리얼 노드 구성 변경
def configure_material_nodes(material):
    # 재질을 사용하기 위해 노드를 활성화
    material.use_nodes = True
    nodes = material.node_tree.nodes

    # 기존 노드를 삭제
    for node in nodes:
        nodes.remove(node)

    # Diffuse Shader 노드 추가
    diffuse_shader = nodes.new(type="ShaderNodeBsdfDiffuse")
    diffuse_shader.location = (0,0)

    # Vertex Color 노드 추가
    vertex_color = nodes.new(type="ShaderNodeVertexColor")
    vertex_color.location = (-300,0)

    # Vertex Color 노드와 Diffuse Shader 노드를 연결
    material.node_tree.links.new(diffuse_shader.inputs["Color"], vertex_color.outputs["Color"])

    # Diffuse Shader 노드와 Material Output 노드를 연결
    material_output = nodes.new(type="ShaderNodeOutputMaterial")
    material_output.location = (300,0)
    material.node_tree.links.new(material_output.inputs["Surface"], diffuse_shader.outputs["BSDF"])
