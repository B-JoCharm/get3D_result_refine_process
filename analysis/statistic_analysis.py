import tkinter as tk
from tkinter import filedialog
import os
import json
import math

def load_json_files(folder_path):
    all_data = []

    # List all files in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                all_data.append(data)

    return all_data

def print_statistic(total_list, num_of_data):

    print("데이터 수 : {}".format(num_of_data))
    print("평균 정점 감소율 : {:.2f} %".format(total_list[0] / num_of_data))
    print("평균 면 감소율 : {:.2f} %".format(total_list[1] / num_of_data))
    print("평균 Edge length cv 감소율 : {:.2f} %".format(total_list[2] / num_of_data))
    print("평균 Area Size cv 감소율 : {:.2f} %".format(total_list[3] / num_of_data))
    print("평균 Face Aspect Ratio average 감소율 : {:.2f} %".format(total_list[4] / num_of_data))
    print("평균 num connected components 감소율 : {:.2f} %".format(total_list[6] / num_of_data))
    print("isolated vertices 갯수")
    print("     개선 전 : {}".format(total_list[7]))
    print("     개선 후 : {}".format(total_list[8]))      
    print("duplicated vertices 갯수")
    print("     개선 전 : {}".format(total_list[9]))
    print("     개선 후 : {}".format(total_list[10]))
    print("duplicated faces 갯수")
    print("     개선 전 : {}".format(total_list[11]))
    print("     개선 후 : {}".format(total_list[12]))
    print("boundary edges 갯수")
    print("     개선 전 : {}".format(total_list[13]))
    print("     개선 후 : {}".format(total_list[14]))
    print("boundary loops 갯수")
    print("     개선 전 : {}".format(total_list[15]))
    print("     개선 후 : {}".format(total_list[16]))
    print("degenerated faces 갯수")
    print("     개선 전 : {}".format(total_list[17]))
    print("     개선 후 : {}".format(total_list[18]))
    print("edge manifold 불만족 갯수")
    print("     개선 전 : {}".format(total_list[19]))
    print("     개선 후 : {}".format(total_list[20]))
    print("vertex manifold 불만족 갯수")
    print("     개선 전 : {}".format(total_list[21]))
    print("     개선 후 : {}".format(total_list[22]))
    print("oriented 불만족 갯수")
    print("     개선 전 : {}".format(total_list[23]))
    print("     개선 후 : {}".format(total_list[24]))
    print()

if __name__ == "__main__":
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open the dialog to choose a folder
    before_folder_path = filedialog.askdirectory()
    after_folder_path = filedialog.askdirectory()

    # Load all JSON files from the selected files
    before_data_list = load_json_files(before_folder_path)
    after_data_list = load_json_files(after_folder_path)

    num_of_data = len(after_data_list)

    total_list = [0] * 25
    before_count_cc = [float('inf'), 0, 0] 

    for i in range(0,num_of_data):
        
        before_num_v = before_data_list[i]['num_vertex']
        after_num_v = after_data_list[i]['num_vertex']
        changed_num_v = ( before_num_v - after_num_v ) / before_num_v
        total_list[0] += changed_num_v * 100

        before_num_f = before_data_list[i]['num_face']
        after_num_f = after_data_list[i]['num_face']
        changed_num_f = ( before_num_f - after_num_f ) / before_num_v
        total_list[1] += changed_num_f * 100

        before_cv_edge_length = math.sqrt(before_data_list[i]['var_Edge Length']) / before_data_list[i]['ave_Edge Length']
        after_cv_edge_length = math.sqrt(after_data_list[i]['var_Edge Length']) / after_data_list[i]['ave_Edge Length']
        changed_cv_edge_length = ( before_cv_edge_length - after_cv_edge_length ) / before_cv_edge_length
        total_list[2] += changed_cv_edge_length * 100

        before_cv_area_size = math.sqrt(before_data_list[i]['var_Area Size']) / before_data_list[i]['ave_Area Size']
        after_cv_area_size = math.sqrt(after_data_list[i]['var_Area Size']) / after_data_list[i]['ave_Area Size']
        changed_cv_area_size = ( before_cv_area_size - after_cv_area_size ) / before_cv_area_size
        total_list[3] += changed_cv_area_size * 100
    
        before_cv_aspect_ratio = before_data_list[i]['ave_Face Aspect Ratio']
        after_cv_aspect_ratio = after_data_list[i]['ave_Face Aspect Ratio']
        changed_cv_aspect_ratio = ( before_cv_aspect_ratio - after_cv_aspect_ratio ) / before_cv_aspect_ratio
        total_list[4] += changed_cv_aspect_ratio * 100

        before_cv_dihedral_angle = math.sqrt(before_data_list[i]['var_Edge Dihedral Angle']) / before_data_list[i]['ave_Edge Dihedral Angle']
        after_cv_dihedral_angle = math.sqrt(after_data_list[i]['var_Edge Dihedral Angle']) / after_data_list[i]['ave_Edge Dihedral Angle']
        changed_cv_dihedral_angle = ( before_cv_dihedral_angle - after_cv_dihedral_angle ) / before_cv_dihedral_angle
        total_list[5] += changed_cv_dihedral_angle * 100

        before_num_cc = before_data_list[i]['num connected components']
        after_num_cc = after_data_list[i]['num connected components']
        changed_num_cc = ( before_num_cc - after_num_cc ) / before_num_cc
        total_list[6] += changed_num_cc * 100
        before_count_cc[0] = min(before_count_cc[0], before_num_cc)
        before_count_cc[1] = max(before_count_cc[1], before_num_cc)
        before_count_cc[2] += before_num_cc

        if before_data_list[i]['num isolated vertices'] > 0 :
            total_list[7] += 1
        if after_data_list[i]['num isolated vertices'] > 0 :
            total_list[8] += 1

        if before_data_list[i]['num duplicated vertices'] > 0 :
            total_list[9] += 1
        if after_data_list[i]['num duplicated vertices'] > 0 :
            total_list[10] += 1

        if before_data_list[i]['num duplicated faces'] > 0 :
            total_list[11] += 1
        if after_data_list[i]['num duplicated faces'] > 0 :
            total_list[12] += 1
   
        if before_data_list[i]['num boundary edges'] > 0 :
            total_list[13] += 1
        if after_data_list[i]['num boundary edges'] > 0 :
            total_list[14] += 1

        if before_data_list[i]['num boundary loops'] > 0 :
            total_list[15] += 1
        if after_data_list[i]['num boundary loops'] > 0 :
            total_list[16] += 1

        if before_data_list[i]['num degenerated faces'] > 0 :
            total_list[17] += 1
        if after_data_list[i]['num degenerated faces'] > 0 :
            total_list[18] += 1     

        if before_data_list[i]['edge manifold'] == False :
            total_list[19] += 1
        if after_data_list[i]['edge manifold'] == False :
            total_list[20] += 1        

        if before_data_list[i]['vertex manifold'] == False :
            total_list[21] += 1
        if after_data_list[i]['vertex manifold'] == False :
            total_list[22] += 1  

        if before_data_list[i]['oriented'] == False :
            total_list[23] += 1
        if after_data_list[i]['oriented'] == False :
            total_list[24] += 1

    print_statistic(total_list, num_of_data)   