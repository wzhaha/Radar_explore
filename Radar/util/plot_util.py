from prettytable import PrettyTable
import matplotlib.pyplot as plt
from util.signal_process_util import *
import matplotlib.cm as cm

'''
打印所有可用天线
'''
def printAntennaPairs(antennaPairs):
    tb = PrettyTable()
    tb.field_names = ["txAntenna", "rxAntenna"]
    for antennna in antennaPairs:
        tb.add_row([antennna.txAntenna, antennna.rxAntenna])
    print(tb)


'''
画出热力图
'''
def drawSpec(signal_records):
    # x = [i for i in range(4096)]
    # y = [i for i in range(100)]
    # X, Y = np.meshgrid(x, y)
    plt.contourf(signal_records, cmap=plt.cm.hot)
    plt.pause(0.001)


'''
画出呼吸波形
'''
def draw_breathe_wave(data):
    plt.figure()
    plt.plot(data)
    plt.show()


'''
画出所有目标
'''
def plot_target_detect(targets):
    x=[]
    y=[]
    z=[]
    for temp in targets:
        x.append(temp.xPosCm)
        y.append(temp.yPosCm)
        z.append(temp.zPosCm)

    ax = plt.axes(projection='3d')
    plt.xlim(-5, 5)
    plt.ylim(-4, 4)
    ax.scatter3D(x, y, z, cmap='Greens')
    plt.pause(0.01)
