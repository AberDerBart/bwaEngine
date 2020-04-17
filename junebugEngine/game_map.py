import json
import pygame
import random
from .tileset import TileSet, EntitySet, SetDict
from .util import relativePath, convertCoords
import os.path
import math
from .text import RenderedText
from .offset_group import OffsetGroup
from .game_object import PHYSICS_SCALE, GameObject
from . import config
from .control import Control


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

        minX = max(math.trunc((0 - offset[0]) / self.gamemap.tileWidth), 0)
        maxX = min(math.ceil((scrWidth - offset[0]) / self.gamemap.tileWidth),
                   self.width-1)
        minY = max(math.trunc((0 - offset[1]) / self.gamemap.tileHeight), 0)
        maxY = min(math.ceil((scrHeight - offset[1]) / self.gamemap.tileHeight),
                   self.height-1)

        for row in range(minY, maxY+1):
            for col in range(minX, maxX+1):
                tile = self.tiles[row][col]
                if tile and tile.getSurf():
                    screen.blit(tile.getSurf(),
                                (col*self.gamemap.tileWidth+offset[0],
                                 row*self.gamemap.tileHeight+offset[1]))


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
        self.tilesH = 0
        self.tilesV = 0
        self.player = None
        self.tileWidth = 0
        self.tileHeight = 0
        self.layers = []
        self.collision = []
        self.goal = None
        self.background = None
        self.collisionTiles = None
        self.layerDict = {}
        self.namedEntities = {}
        self.viewports = set()

        self.chunks = []

        # initialize list for particles
        self.particles = []

    def init(self):
        for entity in self.anchored:
            entity.init()

    def switchToMap(self, newMap):
        viewports = set(self.viewports)

        if viewports:
            Control.setEntity(newMap.player)
            for viewport in viewports:
                viewport.setMap(newMap)

    def spawn(self, objType, position, layer=None, **kwargs):
        entity = objType(world=self, position=position, **kwargs)
        entity.anchorTo(self)

        if entity.sprite:
            layer = layer or self.getLayer("entities")
            layer.entities.add(entity.sprite)

        return entity

    def getLayer(self, layerName):
        return self.layerDict.get(layerName)

    def getEntity(self, entityName):
        return self.namedEntities.get(entityName)

    def pixelWidth(self):
        return self.tileWidth * self.tilesH

    def pixelHeight(self):
        return self.tileHeight * self.tilesV

    def tileAt(self, pos):
        x = pos[0]
        y = pos[1]

        tileX = int(x / self.tileWidth / PHYSICS_SCALE)
        tileY = int(y / self.tileHeight / PHYSICS_SCALE)

        if tileX in range(0, self.tilesH) and tileY in range(0, self.tilesV):
            return self.collisionTiles[tileY][tileX]
        return None

    def tileRange(self, rect):
        xMin = rect.left
        xMax = rect.right - 1
        yMin = rect.top
        yMax = rect.bottom - 1

        tiles = []
        for y in list(range(yMin, yMax,
                            self.tileHeight * PHYSICS_SCALE)) + [yMax]:
            for x in list(range(xMin, xMax,
                                self.tileWidth * PHYSICS_SCALE)) + [xMax]:
                tmpTile = self.tileAt((x, y))
                if tmpTile:
                    tileX = int(x / self.tileWidth / PHYSICS_SCALE) \
                            * self.tileWidth * PHYSICS_SCALE
                    tileY = int(y / self.tileHeight / PHYSICS_SCALE) \
                            * self.tileHeight * PHYSICS_SCALE
                    tileRect = pygame.Rect(tileX,
                                           tileY,
                                           self.tileWidth * PHYSICS_SCALE,
                                           self.tileHeight * PHYSICS_SCALE)
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

    def render(self, screen, offset):
        for layer in self.layers:
            layer.render(screen, offset)
        self.draw_particles(screen, offset)

    def emit_particles(self,
                       center,
                       color_list=[(255, 255, 255)],
                       decay=0.1,
                       x_velocity_range=[-1, 1],
                       y_velocity_range=[-2, 2],
                       radius_range=[1, 4],
                       has_gravity=False):

        physics_center = [center[0] * PHYSICS_SCALE,
                          center[1] * PHYSICS_SCALE]
        x_scaled_range = [x_velocity_range[0] * PHYSICS_SCALE,
                          x_velocity_range[1] * PHYSICS_SCALE]
        y_scaled_range = [y_velocity_range[0] * PHYSICS_SCALE,
                          y_velocity_range[1] * PHYSICS_SCALE]
        x_velocity = random.randint(int(x_scaled_range[0]),
                                    int(x_scaled_range[1]))
        y_velocity = random.randint(int(y_scaled_range[0]),
                                    int(y_scaled_range[1]))
        particle_radius = random.randint(radius_range[0] * PHYSICS_SCALE,
                                         radius_range[1] * PHYSICS_SCALE)

        # compute intervals for colors
        interval_size = particle_radius // len(color_list)
        interval_borders = []
        for ind in range(len(color_list)):
            interval_borders.append(ind * interval_size)
        # create new particle
        self.particles.append([list(physics_center),
                               [x_velocity, y_velocity],
                               particle_radius,
                               particle_radius,
                               color_list,
                               interval_borders,
                               decay * PHYSICS_SCALE,
                               has_gravity])

    def draw_particles(self, surface, offset):
        for particle in self.particles:
            particle_center = [particle[0][0] // PHYSICS_SCALE,
                               particle[0][1] // PHYSICS_SCALE]
            center = list(map(sum, zip(tuple(particle_center), offset)))
            # color stuff
            for ind in range(len(particle[4])):
                if particle[2] >= particle[5][ind]:
                    color_index = ind

            pygame.draw.circle(surface,
                               particle[4][color_index],
                               center,
                               particle[2] // PHYSICS_SCALE)

    def update(self, ms):
        items_to_remove_ = []

        # compute existing particles
        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= particle[6]
            if particle[2] <= 0:
                items_to_remove_.append(particle)
            # simulate gravity for particles
            if particle[7]:
                particle[1][1] += config.gravity * (ms / 1000.)
                if particle[1][1] >= config.max_vertical_speed / 1000.:
                    particle[1][1] = config.max_vertical_speed / 1000.

        # remove nonexistent particles
        for item in items_to_remove_:
            self.particles.remove(item)
