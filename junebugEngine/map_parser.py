import os.path
import json
import junebugEngine.config
from .tileset import EntityData, EntityData, TileSet, Tile, SetDict
from .text import RenderedText
from .sprite import AnimSprite, Alignment
from .game_object import PHYSICS_SCALE, GameObject
import pygame
import math
from . import config
from .util import relativePath
from .parsers import parseProperties
from .parsers.game_object import parseGameObject

from .game_map import GameMap, TileLayer, EntityLayer, PhysicsChunk


class MapParser:
    @staticmethod
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

    @staticmethod
    def _parseEntityLayer(gamemap, entityLayerData, setDict):
        """parses and returns an entity layer of a map"""
        layer = EntityLayer(gamemap, entityLayerData.get("name"))

        for obj in entityLayerData["objects"]:
            sprite = parseGameObject(obj, gamemap, setDict)
            if sprite:
                layer.entities.add(sprite)

        return layer

    @staticmethod
    def _parseBackground(gamemap, backgroundLayerData):
        """parses the background layer of a map and
        adds it to the given GameMap object"""
        gamemap.background = pygame.image.load(relativePath(backgroundLayerData.get("image"),gamemap.path))

    @staticmethod
    def parse(path):
        """parses the map data given under [path] and
        returns the resulting GameMap object"""
        gamemap = GameMap()

        path = os.path.abspath(path)
        gamemap.path = path

        print("Loading map:", path)
        data = json.load(open(path))

        gamemap.tilesH = data['width']
        gamemap.tilesV = data['height']

        renderOrder = data['renderorder']
        gamemap.tileWidth = int(data['tilewidth'])
        gamemap.tileHeight = int(data['tileheight'])

        gamemap.width = gamemap.tilesH * gamemap.tileWidth * PHYSICS_SCALE
        gamemap.height = gamemap.tilesV * gamemap.tileHeight * PHYSICS_SCALE

        for rowIndex in range(math.ceil(gamemap.height / config.chunkSize)):
            row = []
            for colIndex in range(math.ceil(gamemap.width / config.chunkSize)):
                row.append(PhysicsChunk())
            gamemap.chunks.append(row)

        setDict = SetDict(data['tilesets'], path)

        if renderOrder == 'right-down':
            for layer in data["layers"]:
                if layer.get("type") == "tilelayer":
                    newLayer = MapParser._parseTileLayer(gamemap,
                                                         layer,
                                                         setDict)
                    gamemap.layers.append(newLayer)
                    gamemap.layerDict[newLayer.name] = newLayer
                    if not gamemap.collisionTiles:
                        gamemap.collisionTiles = newLayer.tiles
                if layer.get("type") == "objectgroup":
                    newLayer = MapParser._parseEntityLayer(gamemap,
                                                           layer,
                                                           setDict)
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
            gamemap.init()
            return gamemap
        else:
            print("unsupported render order", renderOrder, ", use right-down")
            return None
