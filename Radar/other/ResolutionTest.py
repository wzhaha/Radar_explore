'''
@author 王志
@desc 本段代码通过Raw Signal来大致估算WALABOT的分辨率.使用天线对为1-4.通过观察物体所对应range bin的变化来计算距离分辨率,最终估算结果为2.6mm.
@data 2021/01/07
'''

from __future__ import print_function # WalabotAPI works on both Python 2 an 3.
from sys import platform
from imp import load_source
from os.path import join
import sys
from util.plot_util import *


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
    minInCm, maxInCm, resInCm = 20, 150, 0.1
    # Walabot_SetArenaTheta - input parameters
    minIndegrees, maxIndegrees, resIndegrees = -2, 2, 1
    # Walabot_SetArenaPhi - input parameters
    minPhiInDegrees, maxPhiInDegrees, resPhiInDegrees = -2, 2, 1

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
    print('Start recording')

    while True:
        appStatus, calibrationProcess = wlbt.GetStatus()
        wlbt.Trigger()
        signal = wlbt.GetSignal(usedAntenna)
        signal_records.append(signal[0])

        if len(signal_records)>1:
            # back_signal = np.asarray(signal_records[0])-signal_records[1]
            back_signal = np.asarray(signal_records[-1])- np.asarray(signal_records[0])
            range_bin = np.argmax(back_signal[100:2048])
            print('range_bin is: ', range_bin+100)
            plt.clf()
            plt.plot(back_signal)
            plt.pause(0.01)
            # signal_records.pop(0)


    wlbt.Stop()
    wlbt.Disconnect()
    wlbt.Clean()
    print('Stop recording')


if __name__ == '__main__':
    raw_signal()