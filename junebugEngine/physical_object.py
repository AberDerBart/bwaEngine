import pygame
from pygame.rect import Rect
import json
import operator
from .sprite import AnimSprite, Orientation
from . import config
from enum import Enum
from .util import relativePath, roundAbsUp
from .game_object import GameObject

physicsScale = 1024

class Direction(Orientation):
	NONE = 0
	UP = -1
	DOWN = 1

class PhysicalObject(GameObject):
	typeName = None

	def __init__(self, position, size, **kwargs):
		super().__init__(position, size, **kwargs)

		self.enablePhysics(True)

		self.vx = 0
		self.vy = 0
		self.on_ground = False

	def collideRect(self, block, ms, dx=0, dy=0):
		collisionRect = self.move(dx, dy)
		collision = collisionRect.colliderect(block)

		if collision:
			if dx > 0:
				self.vx = 0
				self.right = block.left
				return Direction.RIGHT
			elif dx < 0:
				self.vx = 0
				self.left = block.right
				return Direction.LEFT
			elif dy < 0:
				self.vy = 0
				self.top = block.bottom
				return Direction.UP
			elif dy > 0:
				self.vy = 0
				self.bottom = block.top
				self.on_ground = True
				return Direction.DOWN
		return Direction.NONE

	def simulate_gravity(self, ms):
		self.vy = self.vy + config.gravity * (ms / 1000.)

		if self.vy >= config.max_vertical_speed / 1000.:
			self.vy = config.max_vertical_speed / 1000.

	def physicsX(self, ms):

		dx = self.vx * ms

		# collide with map in x direction
		if not self.anchor:
			return
		collisionTiles = self.anchor.tileRange(self.move(dx, 0))

		for tile, tileRect in collisionTiles:
			if tile.collide:
				dirX = self.collideRect(tileRect, ms, dx=dx)
				if dirX != Direction.NONE:
					self.on_collision(dirX, None)
					dx = self.vx * ms

		# collide with entities in x direction
		if not self.anchor:
			return
		collision_list = self.anchor.anchored.copy()
		if self in collision_list:
			collision_list.remove(self)

		for block in collision_list:
			dirX = self.collideRect(block, ms, dx=dx)
			if dirX != Direction.NONE:
				self.on_collision(dirX, block)
				block.on_collision(dirX * -1, self)
				dx = self.vx * ms
		
		self.x += dx

	def physicsY(self, ms):

		dy = self.vy * ms

		# collide with map in y direction
		if not self.anchor:
			return

		collisionTiles = self.anchor.tileRange(self.move(0, dy))

		for tile, tileRect in reversed(collisionTiles):
			if tile.collide:
				dirY = self.collideRect(tileRect, ms, dy=dy)
				if dirY != Direction.NONE:
					self.on_collision(dirY, None)
					dy = self.vy * ms

		# collide with entities in y direction
		if not self.anchor:
			return

		collision_list = self.anchor.anchored.copy()
		if self in collision_list:
			collision_list.remove(self)

		for block in collision_list:
			dirY = self.collideRect(block, ms, dy=dy)
			if dirY != Direction.NONE:
				self.on_collision(dirY, block)
				block.on_collision(dirY * -1, self)
				dy = self.vy * ms
		self.y += dy

	def on_collision(self, direction, obj = None):
		pass
	
	def die(self):
		self.anchorTo(None)
		super().die()

	def enablePhysics(self, enable = True):
		self.physics = enable
		if enable:
			pass
			#self.layer.gamemap.physicalEntities.add(self)
		else:
			pass
			#self.remove(self.layer.gamemap.physicalEntities)

	def update(self, ms):
		if(self.physics):
			self.on_ground = False
			self.simulate_gravity(ms)
			
			self.physicsX(ms)
			self.physicsY(ms)
			self.updateSpritePosition()

		super().update(ms)
