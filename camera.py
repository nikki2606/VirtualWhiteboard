#!/usr/bin/env python
# coding: utf-8

import cv2
import time
import numpy as np

#Flattened masking array
cursor = [0,0]
mask = np.array([([False]*160)]*120)
maskSizeSet = False
pointSize = 12
cursorSize = 8
draw = False

def updateMask(img, verbose = False, save = False, label = 'test'):
	global pointSize
	global cursorSize
	global mask
	global cursor
	global draw

	tempImg = np.array(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))

	#Getting index from flattened array
	maxIdx = np.argmax(tempImg.flatten() > 200)
	i,j = int(maxIdx/tempImg.shape[1]) , int(maxIdx%tempImg.shape[1])

	#Normalizing as required
	i,j = int(mask.shape[0] * i/tempImg.shape[0]), int(mask.shape[1] * j/tempImg.shape[1])
	cursor = [i,j]

	if(draw):
		mask[max(0,i-pointSize):min(i+pointSize,img.shape[0]), max(0,j-pointSize):min(j+pointSize,img.shape[1])] = True


class Camera:
	def __init__(self, width, height):
		self.width = width
		self.height = height

	def webcam(self):
		global maskSizeSet
		global mask
		global draw
		global cursor

		cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

		if not cam.isOpened():
			raise IOError("Unable to open webcam")

		cam.set(3, self.width)
		cam.set(4, self.height)

		start = int(round(time.time() * 1000))

		while True:
			#tStart = int(round(time.time() * 1000))
			if int(round(time.time() * 1000)) - start >= 1:
				ret, frame = cam.read()

				if(not maskSizeSet):
					mask = np.array([([False]*frame.shape[1])]*frame.shape[0])
					maskSizeSet = True

				k = cv2.waitKey(33)
				if k == ord('q'):
					break
				elif k == ord('z'): 
					if(not draw):
						#print('Starting Draw')
						draw = True
				elif k == ord('x'):
					if(draw):
						#print('Stopping Draw')
						draw = False

				updateMask(img = frame)
				frame[mask] = [255, 0, 0]
				i,j = cursor[0], cursor[1]
				frame[max(0,i-cursorSize):min(i+cursorSize,frame.shape[0]), max(0,j-cursorSize):min(j+cursorSize,frame.shape[1])] = [0, 255, 0]
				
				cv2.imshow('frame', cv2.flip(frame,1))
				start = int(round(time.time() * 1000))

			#tEnd = int(round(time.time() * 1000))
			#tDiff = tEnd - tStart
			#if(tDiff > 1):
			#	print("Frame Rate: %i"%(1000/tDiff))

		cam.release()
		cv2.destroyAllWindows()


if __name__ == "__main__":
    video = Camera(1920, 1080)
    video.webcam()
    