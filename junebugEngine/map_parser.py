import os.path
import json
import junebugEngine.config
from .tileset import *
from .text import RenderedText
from .camera import Camera
from .sprite import AnimSprite, Alignment
from .game_object import PHYSICS_SCALE, GameObject
import pygame

from .game_map import GameMap, TileLayer, EntityLayer, PhysicsChunk

class MapParser:
	def _parseTileLayer(gamemap, layerData, setDict):
		layer = TileLayer(gamemap, layerData.get("name"))
		layer.height = layerData.get("height")
		layer.width = layerData.get("width")

		for row in range(layer.height):
			curRow = []
			for col in range(layer.width):
				mapIndex = row * layer.width + col
				tileIndex = layerData['data'][mapIndex]
				curRow.append(setDict.get(tileIndex))
			layer.tiles.append(curRow)

		return layer

	def _parseEntityLayer(gamemap, entityLayerData, setDict):
		"""parses and returns an entity layer of a map"""
		layer = EntityLayer(gamemap, entityLayerData.get("name"))

		for obj in entityLayerData["objects"]:
			x = obj["x"]
			y = obj["y"]
			width = obj["width"]
			height = obj["height"]
			if "gid" in obj:
				entityIndex = obj["gid"] & 0x0fffffff # mask out vertical and horizontal flipping
				mirror_h = True if (obj["gid"] & 0x80000000) else False
				entityData = setDict.get(entityIndex)

				# extract static entity properties
				properties = entityData.properties.copy()
				# overwrite custom properties
				propDict = obj.get("properties",[])
				for prop in propDict:
					properties[prop["name"]] = prop["value"]

				generator = entityData.getGenerator()

				entity = None

				if generator:
					try:
						entity = gamemap.spawn(generator, (x * PHYSICS_SCALE, y * PHYSICS_SCALE), layer = layer, **properties)
					except Exception as e:
						print("Error generating type", generator.typeName)
						raise e
					if properties.get("player"):
						gamemap.player = entity

				elif properties.get("sprite"):
					spritePath = relativePath(properties.get("sprite"), entityData.path)
					entity = AnimSprite(spritePath)
					entity.rect.bottomleft = (x,y)
					layer.entities.add(entity)
				else:
					print("Failed to generate",setDict.get(entityIndex).entityType)

			elif "text" in obj:
				layer.entities.add(RenderedText((x,y), obj["text"]))
			elif obj.get("type") == "goal":
				gamemap.goal = GameObject(position=(x * PHYSICS_SCALE, y * PHYSICS_SCALE), size=(width * PHYSICS_SCALE, height * PHYSICS_SCALE), align=Alignment.TOPLEFT)
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
					path.append((px * PHYSICS_SCALE,py * PHYSICS_SCALE))

				cam = Camera(path, timePerPoint, world = gamemap)
				cam.anchorTo(gamemap)

				if player:
					gamemap.player = cam
		return layer

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

		for rowIndex in range(gamemap.height):
			row = []
			for colIndex in range(gamemap.width):
				row.append(PhysicsChunk())
			gamemap.chunks.append(row)

		setDict = SetDict(data['tilesets'], path)
					
		if renderOrder=='right-down':
			for layer in data["layers"]:
				if layer.get("type") == "tilelayer":
					newLayer = MapParser._parseTileLayer(gamemap, layer, setDict)
					gamemap.layers.append(newLayer)
					gamemap.layerDict[newLayer.name] = newLayer
					if not gamemap.collisionTiles:
						gamemap.collisionTiles = newLayer.tiles
				if layer.get("type") == "objectgroup":
					newLayer = MapParser._parseEntityLayer(gamemap, layer, setDict)
					gamemap.layers.append(newLayer)					
					gamemap.layerDict[newLayer.name] = newLayer
				elif layer.get("type") == "imagelayer":
					MapParser._parseBackground(gamemap, layer)
			if not gamemap.getLayer("backgroundEntities"):
				newLayer = EntityLayer(gamemap, 'backgroundEntities')
				gamemap.layers.insert(0, newLayer)
				gamemap.layerDict[newLayer.name] = newLayer
			if not gamemap.getLayer("entities"):
				newLayer = EntityLayer(gamemap, 'entities')
				gamemap.layers.append(newLayer)
				gamemap.layerDict[newLayer.name] = newLayer
			return gamemap
		else:
			print("unsupported render order", renderOrder,", use right-down")
			return None
