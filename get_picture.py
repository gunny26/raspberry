#!/usr/bin/python

# look at this site for more information
# http://www.pygame.org/docs/tut/camera/CameraIntro.html

import pygame
import pygame.camera
from pygame.locals import *
import time

pygame.init()
pygame.camera.init()

# possible values for colorspace: RGB, HSV, YUV all as string
# size greater than 800x600 results in endless get_image() call
cam=pygame.camera.Camera("/dev/video0", (800, 600), "RGB")
cam.start()
# print cam.get_controls()
# default : (False, False, 133)
# lower than 30 is not possible, use get_controls to check
cam.set_controls(hflip=False, vflip=False, brightness=30)
image=cam.get_image()
pygame.image.save(image, "Test.jpg")
