import json
import pygame
from .tileset import TileSet, EntitySet, SetDict
from .util import relativePath, convertCoords
import os.path
import math
from .text import RenderedText
from .offset_group import OffsetGroup
from .game_object import PHYSICS_SCALE, GameObject
from . import config

class MapLayer:
	def __init__(self, gamemap, name):
		self.gamemap = gamemap
		self.name = name
	def render(self, screen, offset):
		pass
	
class TileLayer(MapLayer):
	def __init__(self, gamemap, name):
		self.tiles = []
		self.width = 0
		self.height = 0
		super().__init__(gamemap, name)

	def render(self, screen, offset):

		scrWidth = screen.get_width()
		scrHeight = screen.get_height()

		minX = max(math.trunc((0 - offset[0]) / self.gamemap.tileWidth),0)
		maxX = min(math.ceil((scrWidth - offset[0]) / self.gamemap.tileWidth), self.width-1)
		minY = max(math.trunc((0 - offset[1]) / self.gamemap.tileHeight),0)
		maxY = min(math.ceil((scrHeight - offset[1]) / self.gamemap.tileHeight), self.height-1)

		for row in range(minY,maxY+1):
			for col in range(minX,maxX+1):
				tile = self.tiles[row][col]
				if tile and tile.getSurf():
					screen.blit(tile.getSurf(), (col*self.gamemap.tileWidth+offset[0],row*self.gamemap.tileHeight+offset[1]))
class EntityLayer(MapLayer):
	def __init__(self, gamemap, name):
		self.entities = OffsetGroup()
		super().__init__(gamemap, name)

	def render(self, screen, offset):
		self.entities.draw(screen, offset)

class PhysicsChunk:
	def __init__(self):
		self.objects = []
	def add(self, obj):
		if obj not in self.objects:
			self.objects.append(obj)
	def discard(self, obj):
		if obj in self.objects:
			self.objects.remove(obj)
	def __len__(self):
		return len(self.objects)
	def __iter__(self):
		return self.objects.__iter__()
	def __next__(self):
		return self.objects.__next__()
	
class GameMap(GameObject):
	typeName = "map"
	def __init__(self):
		super().__init__(self)
		self.path = None
		self.width = 0
		self.height = 0
		self.player = None
		self.tileWidth = 0
		self.tileHeight = 0
		self.layers = []
		self.collision = []
		self.goal = None
		self.entities = OffsetGroup()
		self.background = None
		self.collisionTiles = None
		self.layerDict = {}

		self.chunks = []

	def spawn(self, objType, position, layer = None, **kwargs):
		entity = objType(world = self, position = position, **kwargs)
		entity.anchorTo(self)

		if entity.sprite:
			layer = layer or self.getLayer("entities")
			layer.entities.add(entity.sprite)

		return entity
	def getLayer(self, layerName):
		return self.layerDict.get(layerName)
	def pixelWidth(self):
		return self.tileWidth * self.width
	def pixelHeight(self):
		return self.tileHeight * self.height
	def tileAt(self,pos):
		x = pos[0]
		y = pos[1]
		
		tileX = int(x / self.tileWidth / PHYSICS_SCALE)
		tileY = int(y / self.tileHeight / PHYSICS_SCALE)

		if tileX in range(0, self.width) and tileY in range(0, self.height):
			return self.collisionTiles[tileY][tileX]
		return None

	def tileRange(self, rect):
		xMin = rect.left
		xMax = rect.right - 1
		yMin = rect.top
		yMax = rect.bottom - 1

		tiles=[]
		for y in list(range(yMin,yMax,self.tileHeight * PHYSICS_SCALE)) + [yMax]:
			for x in list(range(xMin,xMax,self.tileWidth * PHYSICS_SCALE)) + [xMax]:
				tmpTile=self.tileAt((x,y))
				if tmpTile:
					tileX = int(x / self.tileWidth / PHYSICS_SCALE) * self.tileWidth * PHYSICS_SCALE
					tileY = int(y / self.tileHeight / PHYSICS_SCALE) * self.tileHeight * PHYSICS_SCALE
					tileRect = pygame.Rect(tileX, tileY, self.tileWidth * PHYSICS_SCALE, self.tileHeight * PHYSICS_SCALE)
					tiles.append((tmpTile, tileRect))
		return tiles

	def chunkRange(self, rect):
		xMin = rect.left // config.chunkSize
		xMax = rect.right // config.chunkSize
		yMin = rect.top // config.chunkSize
		yMax = rect.bottom // config.chunkSize

		chunks = []
		for row in self.chunks[yMin: yMax + 1]:
			chunks.extend(row[xMin: xMax+1])
			
		return chunks


	def render(self,screen,offset):
		for layer in self.layers:
			layer.render(screen, offset)

	def update(self, ms):
		#self.entities.update(ms)
		pass
