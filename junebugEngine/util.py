import pygame
import os.path
import junebugEngine.config
import math

def roundAbsUp(number):
	if number < 0:
		return math.floor(number)
	else:
		return math.ceil(number)

def init():
	global font
	font = pygame.font.Font(None,20)
	

def renderFps(screen,tickTime):
	global font
	if(tickTime):
		fps = str(int(1000/tickTime))
	else:
		fps = '9999'
	fontSurface = font.render(fps,False,(255,255,255),(0,0,0))
	screen.blit(fontSurface,(10,10))
	
def relativePath(path, start):
	absStart = os.path.abspath(start)
	dirname = os.path.dirname(absStart)
	resultPath = os.path.join(dirname, path)
	return os.path.abspath(resultPath)
	
def convertCoords(coords):
	if type(coords) == tuple:
		return tuple([x for x in coords])
	else:
		return coords 
