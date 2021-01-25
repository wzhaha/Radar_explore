import matplotlib
import time
import sys
import os
from util.plot_util import *
if os.name == 'nt':
    from msvcrt import getch, kbhit
else:
    import curses

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
from sys import platform
from imp import load_source
from os.path import join
import cv2
import json


if platform == 'win32':
	modulePath = join('C:/', 'Program Files', 'Walabot', 'WalabotSDK',
		'python', 'WalabotAPI.py')
elif platform.startswith('linux'):
    modulePath = join('/usr', 'share', 'walabot', 'python', 'WalabotAPI.py')


'''
模块初始化
'''
wlbt = load_source('WalabotAPI', modulePath)
wlbt.Init()

'''
参数设置
'''
#             R             Phi          Theta
ARENA = [(2, 200, 2), (-45, 45, 3), (-60, 60, 3)]
mtiMode = False
threshold = 0.45 # 在3D中找等高线的阈值

def pol2cart_2D(phi, r):
    '''Convert polar coordinates, in radians, to cartesian'''
    return(r * np.sin(phi), r * np.cos(phi))


def pol2cart_deg_2D(phi, r):
    '''Convert polar coordinates, in degrees, to cartesian'''
    return pol2cart_2D(np.deg2rad(phi), r)


def GenPosMap2D():
    '''Create position coordinates map for plotting'''
    # Phi range vector
    arrP = list(range(*ARENA[1])) + [ARENA[1][1]]

    # R range vector
    arrR = list(range(*ARENA[0])) + [ARENA[0][1]]

    # Format of pmap is [[list of X],[list of Y],[list of dot size]]
    # 将所有的距离和角度一一配对，并将极坐标系转化为笛卡尔坐标系, r*0.75是干嘛的??
    pmap = np.array([list(pol2cart_deg_2D(p, r)) + [r * 0.75] for r in arrR for p in arrP]).transpose()
    return pmap


def TargetSensor2D():
    '''Create position coordinates map for plotting'''
    posmap = GenPosMap2D()
    while True:
        wlbt.Trigger()
        targets = wlbt.GetSensorTargets()
        # M的维度是 r * phi
        M, sizeX, sizeY, sliceDepth, power = wlbt.GetRawImageSlice()
        print('sliceDepth:', sliceDepth)
        # for target in targets:
        #     print('检测到{}个物体: x:{} y:{} z:{}'.format(len(targets), target.xPosCm, target.yPosCm, target.zPosCm))
        s = np.array([val for phi in M for val in phi], dtype=np.float32)
        plt.clf()
        plt.scatter(posmap[0], posmap[1], s=posmap[2], c=s, cmap='autumn')
        plt.pause(0.001)


def pol2cart_3D(theta, phi, r):
    '''Convert polar coordinates, in radians, to cartesian'''
    return(r * np.sin(theta), r * np.cos(theta)*np.sin(phi), r * np.cos(theta)*np.cos(phi))


def pol2cart_deg_3D(theta, phi,  r):
    '''Convert polar coordinates, in degrees, to cartesian'''
    return pol2cart_3D(np.deg2rad(theta), np.deg2rad(phi), r)


def GenPosMap3D():
    '''Create position coordinates map for plotting'''
    # Phi range vector
    arrP = list(range(*ARENA[1])) + [ARENA[1][1]]

    # T range vector
    arrT = list(range(*ARENA[2])) + [ARENA[2][1]]

    # R range vector
    arrR = list(range(*ARENA[0])) + [ARENA[0][1]]

    # Format of pmap is [[list of X],[list of Y],[list of dot size]]
    # 将所有的距离和角度一一配对，并将极坐标系转化为笛卡尔坐标系
    # pmap = np.array([list(pol2cart_deg_3D(t, p, r)) for t in arrT for p in arrP for r in arrR]).transpose()
    pmap = np.array([list(pol2cart_deg_3D(t, p, r)) for t in arrT for p in arrP for r in arrR]).transpose()
    return pmap


def TargetSensor3D():
    '''Create position coordinates map for plotting'''
    posmap = GenPosMap3D()
    front_max_y= max(posmap[0])
    front_max_x= max(posmap[1])

    # plot
    plt.figure()


    '''
        无任何操作：采集1000次，fs大约是1.71
        保存到文本后，采集次数100次，fs大约是1.74
    '''

    json_data = {}
    json_path = '../data/'

    start_time = time.time()
    index = 0
    while index < 100:
        index = index + 1
        wlbt.Trigger()
        # M的维度是： theta * phi * r
        M, _, _, _, _ = wlbt.GetRawImage()
        M = np.array(M)

        draw_list = []
        s = np.array([val for phi_r in M for r in phi_r for val in r], dtype=np.float)
        # 使用标准化后的点去判断是否要画出该点
        for i, temp in enumerate(s):
            if s[i] > 0.15*255:
                posmap_i = posmap[:,i].tolist()
                # 在选出的点中加入他的能量
                posmap_i.append(s[i])
                draw_list.append(posmap_i)

        if len(draw_list) > 0:
            json_data[index] = draw_list

            # # cv2 正面图
            # front_img = np.zeros((int(2 * front_max_y), int(2 * front_max_x), 3), np.uint8) * 255
            # for point in draw_list:
            #     cv2.circle(front_img, (int(-point[1]+front_max_x), int(point[0]+front_max_y)), 5, point[3], -1)
            # front_img = cv2.cvtColor(front_img, cv2.COLOR_BGR2GRAY)
            # # cv2.imwrite('../data/' + str(index) + '_front.png', front_img)
            # plt.imshow(front_img, origin='lower')
            # plt.savefig('../data/' + str(index) + '_front.png')
            print(index, ' yes')
        else:
            print(index, ' no target')
        # 根据时间段将采集的信息保存到json
        if index % 50 == 0:
            fileObject = open(json_path + str(index), 'w+')
            fileObject.write(json.dumps(json_data))
            fileObject.close()  # 最终写入的json文件格式:
            json_data = {}  # 重置列表

    end_time = time.time()
    print('fs is ' ,100/(end_time-start_time))


def normlize(img):
    img = img/ 255
    return img


if __name__ == '__main__':

    # Star Walabot capture process
    print("Initialize API")
    wlbt.Initialize()

    # Check if a Walabot is connected
    try:
        wlbt.ConnectAny()

    except wlbt.WalabotError as err:
        print("Failed to connect to Walabot.\nerror code: " + str(err.code))
        sys.exit(1)

    ver = wlbt.GetVersion()
    print("Walabot API version: {}".format(ver))

    print("Connected to Walabot")
    wlbt.SetProfile(wlbt.PROF_SENSOR)

    # Set scan arena
    wlbt.SetArenaR(*ARENA[0])
    wlbt.SetArenaPhi(*ARENA[1])
    wlbt.SetArenaTheta(*ARENA[2])
    print("Arena set")

    # Set image filter
    '''
    FILTER_TYPE_MTI 的作用，用于检测动态物体，即要成像，还是只检测动的物体
    '''
    filterType = wlbt.FILTER_TYPE_MTI if mtiMode else wlbt.FILTER_TYPE_NONE
    wlbt.SetDynamicImageFilter(filterType)

    '''
        获取所有可以使用的天线对
    '''
    antennaPairs = wlbt.GetAntennaPairs()
    printAntennaPairs(antennaPairs)

    # Start scan
    wlbt.Start()
    # upon any profile change, and is recommended upon possible changes to environment.
    wlbt.StartCalibration()

    stat, prog = wlbt.GetStatus()

    while stat == wlbt.STATUS_CALIBRATING and prog < 100:
        print("Calibrating " + str(prog) + "%")
        wlbt.Trigger()
        stat, prog = wlbt.GetStatus()

    # 画2D俯视图，即slice的切片
    # TargetSensor2D()
    # 画3D图，直接获取image
    TargetSensor3D()

    wlbt.Stop()
    wlbt.Disconnect()
    print("Done!")
    sys.exit(0)