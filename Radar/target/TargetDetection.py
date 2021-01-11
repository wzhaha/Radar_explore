'''
@author 王志
@desc 本段代码使用GetSensorTargets()来对物体进行追踪定位,在设置最远距离为5米的情况下可以追踪,
但是该方法中物体必须是运动的,否则无法测量,因此在很大情况下,出现追踪不到目标的情况.
@data 2021/01/07
'''

from __future__ import print_function # WalabotAPI works on both Python 2 an 3.
from sys import platform
from imp import load_source
from os.path import join
import sys
from util.plot_util import *
import time


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


def target_detection():
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
    wlbt.SetProfile(wlbt.PROF_SENSOR)

    # Walabot_SetArenaR - input parameters
    minInCm, maxInCm, resInCm = 10, 500, 10
    # Walabot_SetArenaTheta - input parameters
    minIndegrees, maxIndegrees, resIndegrees = -20, 20, 4
    # Walabot_SetArenaPhi - input parameters
    minPhiInDegrees, maxPhiInDegrees, resPhiInDegrees = -20, 20, 4

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
    wlbt.SetDynamicImageFilter(wlbt.FILTER_TYPE_MTI)

    '''
    获取所有可以使用的天线对
    '''
    antennaPairs = wlbt.GetAntennaPairs()
    printAntennaPairs(antennaPairs)
    wlbt.Start()
    res=wlbt.GetAdvancedParameter(wlbt.PARAM_CONFIDENCE_FACTOR)

    usedAntenna = antennaPairs[0]
    signal_records = []
    stop = False
    print('Start recording')

    target_pos=[[], [], []]

    while not stop:
        appStatus, calibrationProcess = wlbt.GetStatus()
        wlbt.Trigger()
        # 获取到所有的目标
        targets = wlbt.GetSensorTargets()
        if len(targets) > 0 :
            print('检测到目标')
            for temp in targets:
                print('位置是: x:{} y:{} z: {}'.format(temp.xPosCm, temp.yPosCm, temp.zPosCm))
                dis = math.sqrt(pow(temp.xPosCm, 2) + pow(temp.yPosCm, 2) + pow(temp.zPosCm, 2))
                print('距离为:', round(dis, 2), 'cm')

            # 画出目标的位置
            # plot_target_detect(targets)

            # 尝试在检测到一个目标时对其进行追踪
            if len(targets)==1:
                target_pos[0].append(targets[0].xPosCm)
                target_pos[1].append(targets[0].yPosCm)
                target_pos[2].append(targets[0].zPosCm)
                if len(target_pos[0])>50:
                    target_pos[0].pop(0)
                    target_pos[1].pop(0)
                    target_pos[2].pop(0)

        else:
            print('No target')

        plt.clf()
        plt.xlim(-15, 15)
        plt.ylim(-15, 15)

        # 3D
        ax = plt.axes(projection='3d')
        ax.plot3D(target_pos[0], target_pos[1], target_pos[2], 'gray')

        # 2D
        # plt.plot(target_pos[0], target_pos[1])

        plt.pause(0.01)




    wlbt.Stop()
    wlbt.Disconnect()
    wlbt.Clean()
    print('Stop recording')


if __name__ == '__main__':
    target_detection()