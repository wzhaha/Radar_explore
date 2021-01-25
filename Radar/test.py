import cv2

img = cv2.imread('data/20_front.png', 1)
cv2.imshow('test', img)
cv2.waitKey(0)
img  = cv2.resize(img,(280,350),interpolation=cv2.INTER_AREA)
cv2.imshow('test', img)
cv2.waitKey(0)
