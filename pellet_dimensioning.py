#!/usr/bin/env python3

import cv2
import numpy as np
import matplotlib.pyplot as plt

from imutils import perspective
from imutils import contours
import imutils

img = cv2.imread('fecal_pellet_images/pellet_aruco_test.jpg', cv2.IMREAD_COLOR)
# img = cv2.imread('fecal_pellet_images/20230629_142050.jpg', cv2.IMREAD_COLOR)
# img = cv2.imread('fecal_pellet_images/20230629_145821.jpg', cv2.IMREAD_COLOR)
assert img is not None, "file could not be read, check with os.path.exists()"

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters =  cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

frame = cv2.imread('fecal_pellet_images/pellet_aruco_test.jpg')

markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(frame)
markerIds = markerIds.flatten()
print(markerIds)
print(markerCorners)

### lookup int0 vs intp
int_corners = np.int0(markerCorners)
cv2.polylines(frame, int_corners, True, (254, 8, 192), 5)
cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
cv2.imshow('frame', frame)
cv2.waitKey()

aruco_perimeter = cv2.arcLength(markerCorners[0], True)
pixels2mm = aruco_perimeter / 80
print(aruco_perimeter)

# threshold = 70

# _,thresh = cv2.threshold(img,threshold,255,cv2.THRESH_BINARY_INV)

# lowerb = np.array([16, 25, 38])
# upperb = np.array([48, 74, 104])

lowerb = (2, 5, 37)
upperb = (75, 100, 135)

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

thresh_copy = thresh_bgr
cv2.drawContours(thresh_copy, inner_contours, -1, (255, 255, 255), cv2.FILLED)
cv2.imshow('image', thresh_copy)
cv2.waitKey()

# blurred = cv2.GaussianBlur(thresh_bgr, (5,5), 0)
# cv2.imshow('image', blurred)
# cv2.waitKey()

open_morph_size = 8
kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * open_morph_size + 1, 2 * open_morph_size + 1))
opened = cv2.morphologyEx(thresh_bgr, cv2.MORPH_OPEN, kern)
cv2.imshow('image', opened)
cv2.waitKey()

gray_opened = cv2.cvtColor(opened, cv2.COLOR_BGR2GRAY)
contours, _ = cv2.findContours(gray_opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# bgr_opened = cv2.cvtColor(opened, cv2.COLOR_GRAY2BGR)
# cv2.drawContours(bgr_opened, contours, -1, (254,8,192), 2)

cv2.drawContours(img, contours, -1, (254,8,192), 4)

min_area = 4 * pixels2mm * pixels2mm
max_area = 200 * pixels2mm * pixels2mm

# loop over the contours individually
for c in contours:
	print(cv2.contourArea(c))
	# if the contour is not sufficiently large, ignore it
	if cv2.contourArea(c) < min_area or cv2.contourArea(c) > max_area:
		continue
	# compute the rotated bounding box of the contour
	box = cv2.minAreaRect(c)
	box = cv2.boxPoints(box)
	box = np.array(box, dtype="int")
	# order the points in the contour such that they appear
	# in top-left, top-right, bottom-right, and bottom-left
	# order, then draw the outline of the rotated bounding
	# box
	box = perspective.order_points(box)
	cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 4)
	# loop over the original points and draw them
	for (x, y) in box:
		cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)


# cv2.imshow('image', bgr_opened)
cv2.imshow('image', img)
cv2.waitKey()