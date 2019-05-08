import junebugEngine
import pygame
import argparse

pygame.init()

parser = argparse.ArgumentParser()

parser.add_argument("map")

args = parser.parse_args()

screen = pygame.display.set_mode((640,480))

gameMap = junebugEngine.MapParser.parse(args.map)
viewport = junebugEngine.Viewport((640,480), gameMap)

clock = pygame.time.Clock()

while(True):
	
	viewport.update(clock.tick())
	screen.blit(viewport.surf, (0,0))
	pygame.display.update()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			exit(0)
