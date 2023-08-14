#!/usr/bin/env python3

import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

# load the image
img = cv2.imread('pellet_with_aruco.jpg', cv2.IMREAD_COLOR)
# check that the image exists
assert img is not None, "file could not be read, check with os.path.exists()"

# load the aruco marker settings (the marker on github is 4x4)
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters =  cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)
# detect the aruco marker
markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(img)
# markerIds = markerIds.flatten()
# int_corners = np.intp(markerCorners)

# save the perimeter length of the aruco marker
aruco_perimeter = cv2.arcLength(markerCorners[0], True)
# create a conversion factor based on a 20x20mm aruco marker
pixels2mm = 80 / aruco_perimeter

# code for binary threshold instead of color range
# threshold = 70
# _,thresh = cv2.threshold(img,threshold, 255, cv2.THRESH_BINARY_INV)

# set the upper and lower bound for the pellet color (may need trial and error)
# try using a color picker like https://imagecolorpicker.com/en
# note: color codes are BGR not RGB
lowerb = np.array([1, 2, 3])
upperb = np.array([48, 74, 104])

# some settings that worked for other images in different lighting

# lowerb = (2, 5, 37)
# upperb = (75, 100, 135)

# lowerb = np.array([16, 25, 38])
# upperb = np.array([48, 74, 104])

# threshold the image based on the bounds specified above
thresh = cv2.inRange(img, lowerb, upperb)
# convert the thresholded image back to color (so we can draw in color on it)
thresh_bgr = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

# create an image window
cv2.namedWindow('image', cv2.WINDOW_NORMAL)
# show the raw image
cv2.imshow('image', img)
cv2.waitKey()
# show the thresholded image
cv2.imshow('image', thresh_bgr)
cv2.waitKey()

# find contours in the thresholded image
initial_contours, heirarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
# seperate out inner contours
inner_contours = []
for i in zip(heirarchy[0], initial_contours):
    if i[0][3] > 0:
        inner_contours.append(i[1])
# fill in the inner contours
cv2.drawContours(thresh_bgr, inner_contours, -1, (255, 255, 255), cv2.FILLED)
# show the filled image
cv2.imshow('image', thresh_bgr)
cv2.waitKey()

# gaussian blur may improve some images
# blurred = cv2.GaussianBlur(thresh_bgr, (5,5), 0)
# cv2.imshow('image', blurred)
# cv2.waitKey()

# size for the opening operation ellipse
open_morph_size = 8
# apply the opening operation
kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * open_morph_size + 1, 2 * open_morph_size + 1))
opened = cv2.morphologyEx(thresh_bgr, cv2.MORPH_OPEN, kern)
# show the opened image
cv2.imshow('image', opened)
cv2.waitKey()

# set the opened image to grayscale to find contours
gray_opened = cv2.cvtColor(opened, cv2.COLOR_BGR2GRAY)
contours, _ = cv2.findContours(gray_opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
# draw the contours on the original color image
cv2.drawContours(img, contours, -1, (254,8,192), 4)

# set the minimum and maximum areas for a pellet
min_area = 10 / (pixels2mm * pixels2mm)
max_area = 30 / (pixels2mm * pixels2mm)

# loop over the contours individually
for c in contours:
	# if the contour is not sufficiently large or is too small, ignore it
	if cv2.contourArea(c) < min_area or \
	   cv2.contourArea(c) > max_area:
		continue
	# compute the rotated bounding box of the contour
	box = cv2.minAreaRect(c)
	box = cv2.boxPoints(box)
	box = np.array(box, dtype="int")
	# draw the bounding box
	cv2.drawContours(img, [box.astype("int")], -1, (0, 255, 0), 4)
	# loop over the original points and draw the corners
	for (x, y) in box:
		cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)
	
	# calculate the area in mm
	area = round(cv2.contourArea(c) * pixels2mm * pixels2mm, 2)
	# calculate the 2 edge lengths of the bounding rectangle
	edge1 = round(math.dist(box[0], box [1]) * pixels2mm, 2)
	edge2 = round(math.dist(box[1], box [2]) * pixels2mm, 2)
	# text and locations
	text1 = "area: " + str(area) + " mm^2"
	point1 = [box[1][0], box[1][1] - 80]
	text2 = "rectangle: " + str(edge1) + "mm x " + str(edge2) + "mm"
	point2 = [box[1][0], box[1][1] - 20]
	# add the area and rectangle dimensions to the image
	cv2.putText(img, text1, point1, cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 3)
	cv2.putText(img, text2, point2, cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 3)

# show the final image
cv2.imshow('image', img)
cv2.waitKey()