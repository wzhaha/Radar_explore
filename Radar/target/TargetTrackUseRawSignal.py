'''
@author 王志
@desc 使用多组天线建立坐标系求得物体二维坐标,对物体进行了位置追踪,实现了手写数字和字母。
@data 2021/01/08
'''

from __future__ import print_function # WalabotAPI works on both Python 2 an 3.
from sys import platform
from imp import load_source
from os.path import join
from util.plot_util import *
from scipy.optimize import fsolve
from numpy import *
import sys


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
指定参数
'''
threshold = 0.002 # 背景相减后的最大振幅,如果小于此值,认为没有目标存在
x_min = 4 # 在每组天线算出的x值的差值不可以超过此值
range_bin_resolution = 0.24 # 每个bin对应的距离
xlim_min = -40
xlim_max = 10
ylim_min = 0
ylim_max = 50

'''
从原始信号获取距离
'''
def get_target(signals):
    res = []
    for temp in signals:
        back_data = np.asarray(temp[-1]) - np.asarray(temp[0])
        target_range_bin = np.argmax(back_data)
        max_magnitude = back_data[target_range_bin]
        if max_magnitude > threshold:
            dis = target_range_bin * range_bin_resolution
            res.append(dis)
        else:
            res.append(None)
    return res


'''
方法1:该方程组假设的物体所在坐标系在与雷达顶层齐平的地方
解方程:
'''
def func(paramlist, data):
    x,y=paramlist[0],paramlist[1]
    key = data[2]
    if key == '1-4-18':
        return [
            (x * x + y * y) ** 0.5 + (36 + (x + 8) * (x + 8) + y * y) ** 0.5 - 2 * data[1],
            ((x + 8) * (x + 8) + y * y) ** 0.5 + (36 + (x + 8) * (x + 8) + y * y) ** 0.5 - 2 * data[0]
        ]
    elif key == '17-4-18':
        return [
            (x * x + y * y + 36) ** 0.5 + ((x + 8) * (x + 8) + y * y) ** 0.5 - 2 * data[0],
            (x * x + y * y + 36) ** 0.5 + (x * x + y * y) ** 0.5 - 2 * data[1]
        ]
    elif key == '4-1-17':
        return [
            ((x + 8) * (x + 8) + y * y) ** 0.5 + ((x + 8) * (x + 8) + y * y + 36) ** 0.5 - 2 * data[0],
            ((x + 8) * (x + 8) + y * y) ** 0.5 + (x * x + y * y + 36) ** 0.5 - 2 * data[1]
        ]
    elif key == '4-1-18':
        return [
            ((x + 8) * (x + 8) + y * y) ** 0.5 + ((x + 8) * (x + 8) + y * y + 36) ** 0.5 - 2 * data[0],
            ((x + 8) * (x + 8) + y * y) ** 0.5 + (x * x + y * y) ** 0.5 - 2 * data[1]
        ]
    elif key == '4-17-18':
        return [
            ((x + 8) * (x + 8) + y * y) ** 0.5 + (x * x + y * y + 36) ** 0.5 - 2 * data[0],
            ((x + 8) * (x + 8) + y * y) ** 0.5 + (x * x + y * y) ** 0.5 - 2 * data[1]
        ]
    elif key == '18-1-4':
        return [
            (x * x + y * y) ** 0.5 + ((x + 8) * (x + 8) + y * y + 36) ** 0.5 - 2 * data[0],
            (x * x + y * y) ** 0.5 + ((x + 8) * (x + 8) + y * y) - 2 * data[1]
        ]
    elif key == '18-1-17':
        return [
            (x * x + y * y) ** 0.5 + ((x + 8) * (x + 8) + y * y + 36) ** 0.5 - 2 * data[0],
            (x * x + y * y) ** 0.5 + (x * x + y * y + 36) ** 0.5 - 2 * data[1]
        ]
    elif key == '18-4-17':
        return [
            (x * x + y * y) ** 0.5 + ((x + 8) * (x + 8) + y * y) - 2 * data[0],
            (x * x + y * y) ** 0.5 + (x * x + y * y + 36) ** 0.5 - 2 * data[1]
        ]


'''
方法2:该方程组假设的物体所在坐标系在与雷达中间,即宽度方向的中甲,3cm处
解方程:
'''
def func_new(paramlist, data):
    x,y=paramlist[0],paramlist[1]
    key = data[2]
    if key == '1-4-18':
        return [
            ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 + ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[0],
            ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 + (x ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[1]
        ]
    elif key == '17-4-18':
        return [
            (x ** 2 + y ** 2 + 9) ** 0.5 + ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[0],
            (x ** 2 + y ** 2 + 9) ** 0.5 + (x ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[1]
        ]
    elif key == '4-1-17':
        return [
            ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 + ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[0],
            ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 + (x ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[1]
        ]
    elif key == '4-1-18':
        return [
            ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 + ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[0],
            ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 + (x ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[1]
        ]
    elif key == '4-17-18':
        return [
            ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 + (x ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[0]
            ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 + (x ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[1]
        ]
    elif key == '18-1-4':
        return [
            (x ** 2 + y ** 2 + 9) ** 0.5 + ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[0],
            (x ** 2 + y ** 2 + 9) ** 0.5 + ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[1]
        ]
    elif key == '18-1-17':
        return [
            (x ** 2 + y ** 2 + 9) ** 0.5 + ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[0],
            (x ** 2 + y ** 2 + 9) ** 0.5 + (x ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[0],
        ]
    elif key == '18-4-17':
        return [
            (x ** 2 + y ** 2 + 9) ** 0.5 + ((x + 8) ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[0],
            (x ** 2 + y ** 2 + 9) ** 0.5 + (x ** 2 + y ** 2 + 9) ** 0.5 - 2 * data[0],
        ]


'''
根据两个天线的返回距离,来计算目标位置
'''
def get_target_loc(dis):
    dis_pairs = {
                  '1-4-18': [dis[0], dis[1]],
                  '17-4-18': [dis[2], dis[3]],
                  '4-1-17': [dis[4], dis[5]],
                  '4-1-18': [dis[4], dis[6]],
                  # '4-17-18': [dis[5], dis[6]],
                  # '18-1-4': [dis[7], dis[8]],
                  '18-1-17': [dis[7], dis[9]],
                  '18-4-17': [dis[8], dis[9]],
                  }
    x = []
    y = []
    # 使用scipy解方程
    for key, val in dis_pairs.items():
        if val[0] and val[1]:
            s = fsolve(func_new, [0, 0], args=[val[0], val[1], key])
            x.append(s[0])
            y.append(s[1])
    y = [abs(i) for i in y]

    if len(x)>2:
        x_filter_y = []
        y_filter_y = []
        x = np.asarray(x)
        y = np.asarray(y)
        y_mean = y.mean()
        y_std = y.std()
        # 筛去y轴异常点
        for i,j in zip(x, y):
            if np.abs(j - y_mean) < y_std:
                x_filter_y.append(i)
                y_filter_y.append(j)
        # 找到距离最小的点
        index1, index2 = find_min_dis_index(x_filter_y, x_min)
        if index1 is not None:
            return (x_filter_y[index1]+x_filter_y[index2])/2, (y_filter_y[index1]+y_filter_y[index2])/2
    print('no target')
    return None, None


'''
检查点是否在有效范围内
'''
def check_point(x, y):
    if x > xlim_min and x < xlim_max and y > ylim_min and y < ylim_max:
        return True
    return False


def raw_signal_target_2D():
    # Initializes walabot lib
    wlbt.Initialize()

    # Check if a Walabot is connected
    try:
        wlbt.ConnectAny()
    except wlbt.WalabotError as err:
        print("Failed to connect to Walabot.\nerror code: " + str(err.code))
        sys.exit(1)
    print("Connected to Walabot")

    ver = wlbt.GetVersion()
    print("Walabot API version: {}".format(ver))
    '''
    四种可选参数：
    PROF_SENSOR
    PROF_SENSOR_NARROW
    PROF_SHORT_RANGE_IMAGING
    '''
    '''
    PROF_SENSOR_NARROW下的天线对,其中每两个的水平垂直距离都为2cm
    +-----------+-----------+
    | txAntenna | rxAntenna |
    +-----------+-----------+
    |     1     |     4     |
    |     1     |     17    |
    |     1     |     18    |
    |     17    |     1     |
    |     17    |     4     |
    |     17    |     18    |
    |     4     |     1     |
    |     4     |     17    |
    |     4     |     18    |
    |     18    |     1     |
    |     18    |     4     |
    |     18    |     17    |
    +-----------+-----------+
    '''
    wlbt.SetProfile(wlbt.PROF_SENSOR_NARROW)

    # Walabot_SetArenaR - input parameters
    minInCm, maxInCm, resInCm = 1, 80, 0.1
    # Walabot_SetArenaTheta - input parameters
    minIndegrees, maxIndegrees, resIndegrees = -5, 5, 1
    # Walabot_SetArenaPhi - input parameters
    minPhiInDegrees, maxPhiInDegrees, resPhiInDegrees = -45, 45, 3

    # Setup arena - specify it by Cartesian coordinates.
    wlbt.SetArenaR(minInCm, maxInCm, resInCm)
    # Sets polar range and resolution of arena (parameters in degrees).
    wlbt.SetArenaTheta(minIndegrees, maxIndegrees, resIndegrees)
    # Sets azimuth range and resolution of arena.(parameters in degrees).
    wlbt.SetArenaPhi(minPhiInDegrees, maxPhiInDegrees, resPhiInDegrees)

    '''
    3种filer
    FILTER_TYPE_NONE 
    FILTER_TYPE_MTI 
    FILTER_TYPE_DERIVATIVE
    '''
    wlbt.SetDynamicImageFilter(wlbt.FILTER_TYPE_NONE)

    '''
    获取所有可以使用的天线对
    '''
    antennaPairs = wlbt.GetAntennaPairs()
    printAntennaPairs(antennaPairs)

    '''
    自定义使用的天线对.2对为1组
    '''
    usedAntenna_1_4 = wlbt.AntennaPair(1, 4)
    usedAntenna_1_18 = wlbt.AntennaPair(1, 18)

    usedAntenna_17_4 = wlbt.AntennaPair(17, 4)
    usedAntenna_17_18 = wlbt.AntennaPair(17, 18)

    usedAntenna_4_1 = wlbt.AntennaPair(4, 1)
    usedAntenna_4_17 = wlbt.AntennaPair(4, 17)
    usedAntenna_4_18 = wlbt.AntennaPair(4, 18)

    usedAntenna_18_1 = wlbt.AntennaPair(18, 1)
    usedAntenna_18_4 = wlbt.AntennaPair(18, 4)
    usedAntenna_18_17 = wlbt.AntennaPair(18, 17)


    wlbt.Start()
    '''
    记录天线接收到的原始信号,分别对应1-1, 1-2, ......,4-2
    暂时先使用两对
    '''
    signals = [[], [], [], [], [], [], [], [], [], []]
    print('Start recording')
    # 记录追踪到的物体的位置
    track_x = []
    track_y = []
    no_target_timer = 0
    while True:
        wlbt.Trigger()
        '''
        获取信号并追加到数组
        '''
        signals[0].append(wlbt.GetSignal(usedAntenna_1_4)[0])
        signals[1].append(wlbt.GetSignal(usedAntenna_1_18)[0])

        signals[2].append(wlbt.GetSignal(usedAntenna_17_4)[0])
        signals[3].append(wlbt.GetSignal(usedAntenna_17_18)[0])

        signals[4].append(wlbt.GetSignal(usedAntenna_4_1)[0])
        signals[5].append(wlbt.GetSignal(usedAntenna_4_17)[0])
        signals[6].append(wlbt.GetSignal(usedAntenna_4_18)[0])

        signals[7].append(wlbt.GetSignal(usedAntenna_18_1)[0])
        signals[8].append(wlbt.GetSignal(usedAntenna_18_4)[0])
        signals[9].append(wlbt.GetSignal(usedAntenna_18_17)[0])

        # 目标检测,获取所有天线对检测到的距离物体的距离
        distances = get_target(signals)
        x, y = get_target_loc(distances)

        if x is not None and check_point(x, y):
            no_target_timer = 0
            print('目标位置 x:{}    y:{}'.format(round(x, 2), round(y, 2)))
            track_x.append(x)
            track_y.append(y)
            # sg滤波
            if len(track_x) > 10:
                filter_x = sg_filter(track_x, 5, 3)
            else:
                filter_x = track_x
            plt.clf()
            plt.scatter(filter_x, track_y)
            plt.xlim(xlim_min, xlim_max)
            plt.ylim(ylim_min, ylim_max)
            plt.pause(0.001)
        else:
            no_target_timer =  no_target_timer + 1
            # 大约3秒没有追踪到目标,就清理一下数据
            if no_target_timer > 100:
                # 清空所有数据
                signals = [[], [], [], [], [], [], [], [], [], []]
                track_x.clear()
                track_y.clear()
                plt.clf()
                no_target_timer = 0

    wlbt.Stop()
    wlbt.Disconnect()
    wlbt.Clean()
    print('Stop recording')


if __name__ == '__main__':
    raw_signal_target_2D()