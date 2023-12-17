import os
import json
import math

def save_comparison_data(original_data, refine_data, save_folder, model_name):
    
    # 정점 수 
    before_num_v = original_data['num_vertex']
    after_num_v = refine_data['num_vertex']
    changed_num_v = ( before_num_v - after_num_v ) / before_num_v * 100

    # Face 수
    before_num_f = original_data['num_face']
    after_num_f = refine_data['num_face']
    changed_num_f = ( before_num_f - after_num_f ) / before_num_v * 100
        
    # 엣지 길이 CV
    before_cv_edge_length = math.sqrt(original_data['var_Edge Length']) / original_data['ave_Edge Length']
    after_cv_edge_length = math.sqrt(refine_data['var_Edge Length']) / refine_data['ave_Edge Length']
    changed_cv_edge_length = ( before_cv_edge_length - after_cv_edge_length ) / before_cv_edge_length * 100

    # face 넓이 CV
    before_cv_area_size = math.sqrt(original_data['var_Area Size']) / original_data['ave_Area Size']
    after_cv_area_size = math.sqrt(refine_data['var_Area Size']) / refine_data['ave_Area Size']
    changed_cv_area_size = ( before_cv_area_size - after_cv_area_size ) / before_cv_area_size * 100

    # 종횡비 평균
    before_ave_aspect_ratio = original_data['ave_Face Aspect Ratio']
    after_ave_aspect_ratio = refine_data['ave_Face Aspect Ratio']
    changed_cv_aspect_ratio = ( before_ave_aspect_ratio - after_ave_aspect_ratio ) / before_ave_aspect_ratio * 100

    # 연결요소 변화량
    before_num_cc = original_data['num connected components']
    after_num_cc = refine_data['num connected components']
    changed_num_cc = ( before_num_cc - after_num_cc ) / before_num_cc * 100
        
    text = "-- 최적화 --\n"
    text += "정점 수 변화량 : {:.2f} %\n".format(changed_num_v)
    text += "Face 수 변화량 : {:.2f} %\n\n".format(changed_num_f)

    text += "-- 폴리곤 균일성 변화량 --\n"
    text += "엣지 길이 CV : {:.2f} %\n".format(changed_cv_edge_length)
    text += "Face 넓이 CV : {:.2f} %\n".format(changed_cv_area_size)
    text += "종횡비 평균 : {:.2f} %\n\n".format(changed_cv_aspect_ratio)

    text += "-- 연결요소 변화량 --\n"
    text += "연결요소 변화량 : {:.2f} %\n".format(changed_num_cc)
    
    txt_path = os.path.join(save_folder, "comparison_{}.txt".format(model_name))

    with open(txt_path, 'w') as file:
        file.write(text)
   