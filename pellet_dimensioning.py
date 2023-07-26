#!/usr/bin/env python3

import cv2
import numpy as np
import matplotlib.pyplot as plt

img = cv2.imread('fecal_pellet_images/20230629_142050.jpg', cv2.IMREAD_COLOR)
# img = cv2.imread('fecal_pellet_images/20230629_145821.jpg', cv2.IMREAD_COLOR)
assert img is not None, "file could not be read, check with os.path.exists()"

# threshold = 70

# _,thresh = cv2.threshold(img,threshold,255,cv2.THRESH_BINARY_INV)

lowerb = np.array([16, 25, 38])
upperb = np.array([48, 74, 104])

thresh = cv2.inRange(img, lowerb, upperb)
thresh_bgr = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

cv2.namedWindow('image', cv2.WINDOW_NORMAL)
cv2.imshow('image', img)
cv2.waitKey()

cv2.imshow('image', thresh_bgr)
cv2.waitKey()

initial_contours, heirarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
inner_contours = []
for i in zip(heirarchy[0], initial_contours):
    if i[0][3] > 0:
        inner_contours.append(i[1])
print(inner_contours)

thresh_copy = thresh_bgr
cv2.drawContours(thresh_copy, inner_contours, -1, (255, 255, 255), cv2.FILLED)
cv2.imshow('image', thresh_copy)
cv2.waitKey()

open_morph_size = 8
kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * open_morph_size + 1, 2 * open_morph_size + 1))
opened = cv2.morphologyEx(thresh_bgr, cv2.MORPH_OPEN, kern)
cv2.imshow('image', opened)
cv2.waitKey()

contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# bgr_opened = cv2.cvtColor(opened, cv2.COLOR_GRAY2BGR)
# cv2.drawContours(bgr_opened, contours, -1, (254,8,192), 2)

cv2.drawContours(opened, contours, -1, (254,8,192), 2)

# cv2.imshow('image', bgr_opened)
cv2.imshow('image', opened)
cv2.waitKey()