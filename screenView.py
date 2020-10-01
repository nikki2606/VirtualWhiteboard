import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from ctypes import *
import numpy as np
import cv2

settings = {
	'screenWidth': 1366,
	'screenHeight': 768,
	'canvasWidth': 192,
	'canvasHeight': 108,
	'screenZ': -2,
  'translateSpeed' : 0.06,
  'rotateSpeed' : 0.08,
  'threshold' : 200,
  'useThreshold' : True
}

import random

cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cam.isOpened():
  raise IOError("Unable to open webcam")

#cam.set(3, 192)
#cam.set(4, 108)

cam.set(3, 64)
cam.set(4, 32)

globalI = 0
globalJ = 0
def nextPixels():
  global globalI
  global globalJ
  globalJ += 1
  if(globalJ == settings['canvasHeight']):
    globalJ = 0
    globalI += 1
  return(globalI, globalJ, 0)

def randomPixelInCanvas():
  i,j = random.randint(0, settings['canvasWidth']-1), random.randint(0, settings['canvasHeight']-1)
  return(i, j, 0)

cursor = (0,0)
drawPixels = []
pixelVertices = []

def runLoop(verbose = False):
  global settings
  global cursor
  global drawPixels
  global pixelVertices

  if(verbose):
    print('Initializing Screen')

  pygame.init()
  display = (settings['screenWidth'],settings['screenHeight'])
  pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
  
  gluPerspective(60, (display[0]/display[1]), 0.1, 999)
  glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

  glTranslatef(-settings['canvasWidth']/2,-settings['canvasHeight']/2,-90)
  glClearColor(0.3, 0.2, 0.2, 0.2)
  glEnable(GL_DEPTH_TEST)

  if(verbose):
    print('Starting Gameloop')

  glEnableClientState(GL_VERTEX_ARRAY)
  VBO = glGenBuffers(1)
  glBindBuffer(GL_ARRAY_BUFFER, VBO)

  while(True):
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
          pygame.quit()
          quit()

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          cam.release()
          cv2.destroyAllWindows()
          pygame.quit()
          quit()

    keys = pygame.key.get_pressed()
    
    
    ret, frame = cam.read()
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    x,y = 0,0
    intensity = 0
    flag = False
    for i in range(frame.shape[0]):
      for j in range(frame.shape[1]):
        if(settings['useThreshold'] and intensity > settings['threshold']):
          y, x = i, j
          flag = True

        if(flag):
          break

        if intensity < gray[i, j]:
          y, x = i, j
          intensity = gray[i, j]

      if(flag):
        break

    x = settings['canvasWidth'] - (x/frame.shape[1]) * settings['canvasWidth']
    y = settings['canvasHeight'] - (y/frame.shape[0]) * settings['canvasHeight']

    cursor = (x, y)
    pixel = (x, y, 0)

    if(keys[pygame.K_SPACE] and pixel not in drawPixels):
      i,j,k = pixel[0], pixel[1], pixel[2]
      drawPixels.append((i,j,k))
      pixelVertices.extend(pixel)

    if keys[pygame.K_w]:
      glTranslatef(0,0,settings['translateSpeed'])

    if keys[pygame.K_s]:
      glTranslatef(0,0,-settings['translateSpeed'])

    if keys[pygame.K_a]:
      glTranslatef(settings['translateSpeed'],0,0)

    if keys[pygame.K_d]:
      glTranslatef(-settings['translateSpeed'],0,0)

    if keys[pygame.K_r]:
      glTranslatef(0,-settings['translateSpeed'],0)

    if keys[pygame.K_f]:
      glTranslatef(0,settings['translateSpeed'],0)

    if keys[pygame.K_q]:
      glRotatef(settings['rotateSpeed'],0,1,0)  
    
    if keys[pygame.K_e]:
      glRotatef(settings['rotateSpeed'],0,-1,0)

    pygame.display.flip()
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glColor3f(0.2,0.8,0.7)
    glPointSize(20)
    glBufferData(GL_ARRAY_BUFFER,
      len(pixelVertices)*4,
      (c_float*len(pixelVertices))(*pixelVertices), 
      GL_DYNAMIC_COPY
    )
    (1,2,3),(4,5,6)
    glVertexPointer(3, GL_FLOAT, 0, None)
    glDrawArrays(GL_POINTS, 0, len(pixelVertices))


    glColor3f(0.2,0.6,0.8)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    glVertex3f(cursor[0]-1, cursor[1]-1, 1)
    glVertex3f(cursor[0]-1, cursor[1]+1, 1)
    glVertex3f(cursor[0]+1, cursor[1]+1, 1)
    glVertex3f(cursor[0]+1, cursor[1]-1, 1)
    glEnd()
    #pygame.time.wait(16)
    
runLoop(verbose = True)