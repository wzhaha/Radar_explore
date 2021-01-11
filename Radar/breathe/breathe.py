from __future__ import print_function # WalabotAPI works on both Python 2 an 3.
from sys import platform
from imp import load_source
from os.path import join
import matplotlib.pyplot as plt

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
其他参数列表
'''
# Fs = 100 # 采样率

'''
画出呼吸波形
'''
breathe_data = []
plt.xlim(0,100)
def DrawBreathingEnergy(energy):
    temp =  energy * 1e7
    breathe_data.append(temp)
    if len(breathe_data)>100:
        breathe_data.pop(0)
        # breathe_rate = cal_breathe_rate(breathe_data, Fs)
        # print('breathe rate:' + str(breathe_rate))
    plt.clf()
    plt.plot(breathe_data)
    plt.pause(0.001)


def BreathingApp():
    # Walabot_SetArenaR - input parameters
    minInCm, maxInCm, resInCm = 30, 100, 0.1
    # Walabot_SetArenaTheta - input parameters
    minIndegrees, maxIndegrees, resIndegrees = -4, 4, 2
    # Walabot_SetArenaPhi - input parameters
    minPhiInDegrees, maxPhiInDegrees, resPhiInDegrees = -4, 4, 2
    # Initializes walabot lib
    wlbt.Initialize()
    # 1) Connect : Establish communication with walabot.
    wlbt.ConnectAny()
    # 2) Configure: Set scan profile and arena
    # Set Profile - to Sensor-Narrow.
    wlbt.SetProfile(wlbt.PROF_SENSOR_NARROW)
    # Setup arena - specify it by Cartesian coordinates.
    wlbt.SetArenaR(minInCm, maxInCm, resInCm)
    # Sets polar range and resolution of arena (parameters in degrees).
    wlbt.SetArenaTheta(minIndegrees, maxIndegrees, resIndegrees)
    # Sets azimuth range and resolution of arena.(parameters in degrees).
    wlbt.SetArenaPhi(minPhiInDegrees, maxPhiInDegrees, resPhiInDegrees)
    # Dynamic-imaging filter for the specific frequencies typical of breathing
    wlbt.SetDynamicImageFilter(wlbt.FILTER_TYPE_DERIVATIVE)
    # 3) Start: Start the system in preparation for scanning.
    wlbt.Start()
    # 4) Trigger: Scan (sense) according to profile and record signals to be
    # available for processing and retrieval.
    while True:
        appStatus, calibrationProcess = wlbt.GetStatus()
        # 5) Trigger: Scan(sense) according to profile and record signals
        # to be available for processing and retrieval.
        wlbt.Trigger()
        # 6) Get action: retrieve the last completed triggered recording
        energy = wlbt.GetImageEnergy()
        DrawBreathingEnergy(energy)
    # 7) Stop and Disconnect.
    wlbt.Stop()
    wlbt.Disconnect()
    wlbt.Clean()
    print('Terminate successfully')



if __name__ == '__main__':
    BreathingApp()
