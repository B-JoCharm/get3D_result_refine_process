import os
import bpy

# 카메라 세팅 함수
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

#광원 세팅 함수
def light_setting(light, location):
    if light:
        # 광원의 위치를 변경합니다.
        light.location = location  

        # 변경된 위치를 적용합니다.
        bpy.context.view_layer.update()

    else:
        print("광원을 찾을 수 없습니다. 이름을 확인하십시오.")

# 메시 불러오기 및 초기설정(불러온 객체 선택 및 활성화, 스케일조정), imported_objs로 선택된 객체 리스트를 반환함에 따라 불러온 객체를 다시 선택할때 사용 가능
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
    bpy.context.object.scale[0] = 1
    bpy.context.object.scale[1] = 1
    bpy.context.object.scale[2] = 1
    
    return imported_objs


def parse_mtl(mtl_file):
    values = {}
    with open(mtl_file, 'r') as file:
        for line in file:
            if line.startswith('newmtl'):
                continue
            split_line = line.strip().split()
            if split_line:
                key = split_line[0]
                if key in ['Ns', 'Ka', 'Kd', 'Ks', 'Ni', 'd']:
                    values[key] = tuple(map(float, split_line[1:]))
    return values

# 재질 및 텍스처 적용 (텍스처 파일이 있는 경우에만 사용 가능)
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

