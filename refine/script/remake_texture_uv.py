import bpy
import os

def remake_texture_uv(model_name ,output_directory):
    # 모델 선택
    model = bpy.data.objects[model_name]
    bpy.context.view_layer.objects.active = model
    model.select_set(True)

    # 새 UV맵 생성 및 Smart UV Project 실행
    bpy.ops.mesh.uv_texture_add()
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')

    # 렌더 엔진을 Cycles로 설정 및 베이크 설정
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.bake_type = 'DIFFUSE'
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False

    # 베이크 실행
    bpy.ops.object.bake(type='DIFFUSE')

    # 기존 UV 맵 제거
    if "UVMap" in model.data.uv_layers:
        model.data.uv_layers.remove(model.data.uv_layers["UVMap"])

    # 베이크된 이미지 찾기 및 저장
    baked_image = None
    for mat_slot in model.material_slots:
        if mat_slot.material and mat_slot.material.use_nodes:
            for node in mat_slot.material.node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    baked_image = node.image
                    break
            if baked_image:
                break

    if baked_image:
        # 새 파일 경로 설정
        new_image_path = os.path.join(output_directory, f"{model_name}.png")
        baked_image.filepath_raw = new_image_path
        baked_image.file_format = 'PNG'
        baked_image.save()
        print(f"Baked image saved to {new_image_path}")
    else:
        print("Baked image not found.")