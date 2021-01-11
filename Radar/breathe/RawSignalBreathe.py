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


def raw_signal():
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
    wlbt.SetProfile(wlbt.PROF_SENSOR_NARROW)

    # Walabot_SetArenaR - input parameters
    minInCm, maxInCm, resInCm = 20, 100, 0.1
    # Walabot_SetArenaTheta - input parameters
    minIndegrees, maxIndegrees, resIndegrees = -4, 4, 2
    # Walabot_SetArenaPhi - input parameters
    minPhiInDegrees, maxPhiInDegrees, resPhiInDegrees = -4, 4, 2

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
    wlbt.Start()
    res=wlbt.GetAdvancedParameter(wlbt.PARAM_CONFIDENCE_FACTOR)

    usedAntenna = antennaPairs[0]
    signal_records = []
    stop = False
    print('Start recording')

    time_start = time.time()  # 开始计时

    while not stop:
        appStatus, calibrationProcess = wlbt.GetStatus()
        wlbt.Trigger()
        signal = wlbt.GetSignal(usedAntenna)
        signal_records.append(signal[0])
        plt.clf()
        plt.plot(signal[1], signal[0])
        plt.pause(0.001)

        if len(signal_records)==200:
            stop=True

    time_end = time.time()  # 结束计时

    time_c = time_end - time_start  # 运行所花时间
    print('Fs:', str(200/time_c))

    wlbt.Stop()
    wlbt.Disconnect()
    wlbt.Clean()
    print('Stop recording')

    # 背景相减
    back_signal_records = back_substraction(signal_records)
    # 画热力图
    drawSpec(back_signal_records)
    # 取呼吸波形
    breathe_data = get_breathe_data(back_signal_records)
    # 画呼吸波形
    draw_breathe_wave(breathe_data)



if __name__ == '__main__':
    raw_signal()