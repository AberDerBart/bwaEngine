import os.path
import json
import junebugEngine.config
from .tileset import *
from .text import RenderedText
from .camera import Camera
import pygame

from .game_map import GameMap

class MapParser:
	def _parseMap(gamemap, mapLayerData, setDict):
		"""parses the map layer of a map and adds it to the given GameMap object"""
		for row in range(gamemap.height):
			curRow = []
			for col in range(gamemap.width):
				mapIndex = row * gamemap.width + col
				tileIndex = mapLayerData['data'][mapIndex]
				curRow.append(setDict.get(tileIndex))
			gamemap.tiles.append(curRow)

	def _parseEntities(gamemap, entityLayerData, setDict):
		"""parses the entity layer of a map and adds it to the given GameMap object"""
		for obj in entityLayerData["objects"]:
			x = obj["x"]
			y = obj["y"]
			width = obj["width"]
			height = obj["height"]
			if "gid" in obj:
				entityIndex = obj["gid"]
				entityData = setDict.get(entityIndex)
				generator = entityData.getGenerator()
				if generator:
					entity = generator(gamemap, (x,y))

					propDict = obj.get("properties",[])
					properties = entityData.properties.copy()
					for prop in propDict:
						properties[prop["name"]] = prop["value"]
					if properties.get("player"):
						gamemap.player = entity
				else:
					print("Failed to generate",setDict.get(entityIndex).entityType)
			elif "text" in obj:
				gamemap.entities.add(RenderedText((x,y), obj["text"]))
			elif obj.get("type") == "goal":
				gamemap.goal = pygame.Rect(x, y, width, height)
			elif obj.get("type") == "camera":

				properties = obj["properties"]
				player = False
				timePerPoint = 10

				for prop in properties:
					if prop["name"] == "player":
						player = prop.get("value")
					if prop["name"] == "timePerPoint":
						timePerPoint = prop.get("value")

				path = []

				for point in obj["polyline"]:
					px = point["x"]
					py = point["y"]
					path.append((px,py))

				cam = Camera(gamemap, path, timePerPoint)
				gamemap.entities.add(cam)

				if player:
					gamemap.player = cam

	def _parseBackground(gamemap, backgroundLayerData):
		"""parses the background layer of a map and adds it to the given GameMap object"""
		gamemap.background = pygame.image.load(relativePath(backgroundLayerData.get("image"),gamemap.path))

	def parse(path):
		"""parses the map data given under [path] and returns the resulting GameMap object"""
		gamemap = GameMap()

		path = os.path.abspath(path)
		gamemap.path = path

		print("Loading map:",path)
		data = json.load(open(path))

		gamemap.width = data['width']
		gamemap.height = data['height']


		renderOrder = data['renderorder']
		gamemap.tileWidth = int(data['tilewidth'])
		gamemap.tileHeight = int(data['tileheight'])

		setDict = SetDict(data['tilesets'], path)
					
		if renderOrder=='right-down':
			for layer in data["layers"]:
				if layer.get("type") == "tilelayer":
					MapParser._parseMap(gamemap, layer, setDict)
				if layer.get("type") == "objectgroup":
					MapParser._parseEntities(gamemap, layer, setDict)
				elif layer.get("type") == "imagelayer":
					MapParser._parseBackground(gamemap, layer)
			return gamemap
		else:
			print("unsupported render order", renderOrder,", use right-down")
			return None
