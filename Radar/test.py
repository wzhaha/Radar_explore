import sympy
import time
from scipy.optimize import fsolve

# 方法1
dis1 = 18.2
dis2 = 19.24
x,y = sympy.symbols("x y")
start_time = time.time()
a = sympy.solve([(x * x + y * y + 36) ** 0.5 + ((x + 8) * (x + 8) + y * y) ** 0.5 - 2 * dis1,
            (x * x + y * y + 36) ** 0.5 + (x * x + y * y) ** 0.5 - 2 * dis2],[x,y])
end_time = time.time()
print(a)
print('method1 time is {}'.format(end_time-start_time))



# # 方法2
# def func(paramlist, data):
#     x,y=paramlist[0],paramlist[1]
#     return [ (x*x + y*y)**0.5+(64+(x-10)*(x-10)+y*y)**0.5-2*data[1],
#             ((x-10)*(x-10) + y*y)**0.5+(64+(x-10)*(x-10)+y*y)**0.5-2*data[0]]
#
# start_time = time.time()
# s = fsolve(func, [0, 0], args=[10, 10])
# end_time = time.time()
# print(s)
# print('method2 time is {}'.format(end_time-start_time))


'''
使用方差去判断异常点
'''
# x = np.asarray(x)
# y = np.asarray(y)
# x_mean = x.mean()
# y_mean = y.mean()
# x_std = x.std()
# y_std = y.std()
#
# x_ = [i for i in x if np.abs(i-x_mean)<x_std]
# y_ = [i for i in y if np.abs(i-y_mean)<y_std]
# if len(x_) > 0 and len(y_) > 0:
#     return mean(x_), mean(y_)