import json
import os
from target.TargetTrackUseRawImage import GenPosMap3D
import numpy as np
import cv2
import matplotlib.pyplot as plt


data_path = '../data/'
pic_path = '../data/heat_pic/'

posmap = GenPosMap3D()
front_max_y = max(posmap[0])
front_max_x = max(posmap[1])

side_max_y = max(posmap[0])
side_max_x = max(posmap[2])

# 将采集的json数据转化为图片
def json2pic(data_path, pic_path):
    files = os.listdir(data_path)
    for filename in files:
        file_path = os.path.join(data_path, filename)
        if not os.path.isdir(file_path):
            # 打开该文件
            with open(file_path, 'r') as load_f:
                load_dict = json.load(load_f)
            for index, val in load_dict.items():
                draw_list = np.asarray(val)
                # 正视图
                front_img = np.zeros((int(2 * front_max_y), int(2 * front_max_x), 3), np.uint8) * 255
                for point in draw_list:
                    cv2.circle(front_img, (int(-point[1]+front_max_x), int(point[0]+front_max_y)), 5, point[3], -1)
                front_img = cv2.cvtColor(front_img, cv2.COLOR_BGR2GRAY)
                plt.clf()
                plt.imshow(front_img, origin='lower')
                plt.axis('off')
                plt.xticks([])
                plt.yticks([])
                plt.savefig(pic_path + str(index) + '_front.png')
                # 侧视图
                side_img = np.zeros((int(2 * side_max_y), int(2 * front_max_x), 3), np.uint8) * 255
                for point in draw_list:
                    cv2.circle(side_img, (int(point[2]), int(point[0] + side_max_y)), 5, point[3], -1)
                side_img = cv2.cvtColor(side_img, cv2.COLOR_BGR2GRAY)
                plt.clf()
                plt.imshow(side_img, origin='lower')
                plt.axis('off')
                plt.xticks([])
                plt.yticks([])
                plt.savefig(pic_path + str(index) + '_side.png')


json2pic(data_path, pic_path)