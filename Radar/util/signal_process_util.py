import numpy as np
from scipy.fftpack import fft
import math
import numpy as np


'''
快速傅里叶变换
@:param data 序列数据
@:param Fs 采样率
'''
def FFT (data, Fs):
    L = len (data)                          # 信号长度
    N =np.power(2,np.ceil(np.log2(L)))      # 下一个最近二次幂
    FFT_y = (fft(data,int(N)))/L*2                  # N点FFT，但除以实际信号长度 L
    Fre = np.arange(int(N/2))*Fs/N          # 频率坐标
    FFT_y = FFT_y[range(int(N/2))]          # 取一半
    return Fre, FFT_y


'''
根据呼吸波形求呼吸速率
@:param data 序列数据
@:param Fs 采样率
'''
def cal_breathe_rate(data, Fs):
    Fre, FFT_y = FFT(data, Fs)
    FFT_y =  [math.sqrt(pow(temp.real, 2)+pow(temp.imag, 2)) for temp in FFT_y]
    index=FFT_y.index(max(FFT_y[4:]))
    return Fre[index+4]


'''
back_substraction
@:param signals 信号序列
'''
def back_substraction(signal_records):
    res = []
    signal_0 = np.asarray(signal_records[0])
    for temp in signal_records:
        res.append(np.asarray(temp)-signal_0)
    return np.asarray(res)


'''
获取目标所在bin
'''
def get_range_bin(data):
    add_pos_data = data.sum(axis=0)
    # 求出最大值的位置
    max_pos = np.argmax(add_pos_data)
    return max_pos


'''
在背景相减后的波形上获取得到人体所在位置,并提取呼吸波形
'''
def get_breathe_data(data):
    add_pos_data = data.sum(axis=0)
    # 求出最大值的位置
    max_pos = np.argmax(add_pos_data)
    return data[:, max_pos]


'''
找打数组中距离最近的两个点的index
'''
def find_min_dis_index(data, threadsold):
    index1 = -1
    index2 = -1
    length = len(data)
    min_dis = threadsold
    for i in range(length):
        for j in range(i+1, length):
            dis = abs(data[i]-data[j])
            if  dis < min_dis:
                index1 = i
                index2 = j
                min_dis = dis
    if min_dis != threadsold:
        return index1, index2
    return None, None


'''
SG滤波
'''
def sg_filter(data, window_size, order):
    if window_size % 2 == 0 or window_size == 0:
        window_size += 1

    arr = []
    step = int((window_size - 1) / 2)
    for i in range(window_size):
        a = []
        for j in range(order):
            y_val = np.power(-step + i, j)
            a.append(y_val)
        arr.append(a)

    arr = np.mat(arr)
    arr = arr * (arr.T * arr).I * arr.T

    a = np.array(arr[step])
    a = a.reshape(window_size)

    data = np.insert(data, 0, [data[0] for i in range(step)])
    data = np.append(data, [data[-1] for i in range(step)])

    qlist = []
    for i in range(step, data.shape[0] - step):
        arra = []
        for j in range(-step, step + 1):
            arra.append(data[i + j])
        b = np.sum(np.array(arra) * a)
        qlist.append(b)
    return qlist


# data = [1,2,1,1,2,1,2,1,2]
# res = sg_filter(data, 5, 4)
# print(res)
# import matplotlib.pyplot as plt
# plt.plot(data)
# plt.plot(res)
# plt.show()