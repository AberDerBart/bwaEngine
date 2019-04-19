import json
import pygame
from tileset import TileSet, EntitySet, SetDict
from util import relativePath, convertCoords
import os.path
import math
import config
import physical_object
from text import RenderedText
from offset_group import OffsetGroup

def test_map(filename, offset=(0,0)):
	pygame.init()
	screen = pygame.display.set_mode((960,544))

	testMap = GameMap(filename,2.4535)

	testMap.render(screen,offset)

	pygame.display.update()
	
	while(True):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit(0)

	

class GameMap:
	def __init__(self):
		self.path = None
		self.width = 0
		self.height = 0
		self.player = None
		self.tileWidth = 0
		self.tileHeight = 0
		self.tiles = []
		self.goal = None
		self.entities = OffsetGroup()
		self.physicalEntities = pygame.sprite.Group()
		self.background = None
		
	def pixelWidth(self):
		return self.tileWidth * self.width
	def pixelHeight(self):
		return self.tileHeight * self.height
	def tileAt(self,pos):
		x = pos[0]
		y = pos[1]
		
		tileX = int(x / self.tileWidth)
		tileY = int(y / self.tileHeight)

		if tileX in range(0, self.width) and tileY in range(0, self.height):
			return self.tiles[tileY][tileX]
		return None

	def tileRange(self, rect):
		xMin = rect.left
		xMax = rect.right - 1
		yMin = rect.top
		yMax = rect.bottom - 1

		tiles=[]
		for y in list(range(yMin,yMax,self.tileHeight)) + [yMax]:
			for x in list(range(xMin,xMax,self.tileWidth)) + [xMax]:
				tmpTile=self.tileAt((x,y))
				if tmpTile:
					tileX = int(x / self.tileWidth) * self.tileWidth
					tileY = int(y / self.tileHeight) * self.tileHeight
					tileRect = pygame.Rect(tileX, tileY, self.tileWidth, self.tileHeight)
					tiles.append((tmpTile, tileRect))
		return tiles

	def render(self,screen,offset):
		scrWidth = screen.get_width()
		scrHeight = screen.get_height()

		minX = max(math.trunc((0 - offset[0]) / self.tileWidth),0)
		maxX = min(math.ceil((scrWidth - offset[0]) / self.tileWidth), self.width-1)
		minY = max(math.trunc((0 - offset[1]) / self.tileHeight),0)
		maxY = min(math.ceil((scrHeight - offset[1]) / self.tileHeight), self.height-1)
		
		for row in range(minY,maxY+1):
			for col in range(minX,maxX+1):
				tile = self.tiles[row][col]
				if tile and tile.getSurf():
					screen.blit(tile.getSurf(), (col*self.tileWidth+offset[0],row*self.tileHeight+offset[1]))
		self.entities.draw(screen, offset)

	def clear(self,screen,bg,offset):
		scrWidth = screen.get_width()
		scrHeight = screen.get_height()

		minX = max(math.trunc((0 - offset[0]) / self.tileWidth),0)
		maxX = min(math.ceil((scrWidth - offset[0]) / self.tileWidth), self.width-1)
		minY = max(math.trunc((0 - offset[1]) / self.tileHeight),0)
		maxY = min(math.ceil((scrHeight - offset[1]) / self.tileHeight), self.height-1)

		for row in range(minY,maxY+1):
			for col in range(minX,maxX+1):
				tile = self.tiles[row][col]
				if tile:
					left = max(col * self.tileWidth + offset[0], 0)
					top = max(row *self.tileHeight + offset[1], 0)
					
					right = min(scrWidth, left + self.tileWidth)
					bottom = min(scrHeight, top + self.tileHeight)

					pos = (left,top)
					size = (right - left, bottom - top)
					print(pos)
					screen.blit(bg.subsurface(pygame.Rect(pos,size)),pos)

		self.entities.clear(screen, bg)

	def update(self, ms):
		#self.entities.update(ms)
		pass
