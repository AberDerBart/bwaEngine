import junebugEngine
import pygame
import argparse

pygame.init()

parser = argparse.ArgumentParser()

parser.add_argument("map")

args = parser.parse_args()

screen = pygame.display.set_mode((1366,768))

gameMap = junebugEngine.MapParser.parse(args.map)

gameMap.render(screen,(0,0))
pygame.display.update()

while(True):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			exit(0)
