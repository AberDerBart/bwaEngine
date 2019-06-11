import pygame
import json
import operator
from .sprite import AnimSprite, Orientation
from . import config
from enum import Enum
from .util import relativePath, roundAbsUp

class Direction(Orientation):
	NONE = 0
	UP = -1
	DOWN = 1

class PhysicalObject(AnimSprite):
	typeName = None

	def __init__(self, json_sprite, physical_data, layer, initial_position, mirror_h, **kwargs):
		super().__init__(json_sprite, layer, initial_position, mirror_h, **kwargs)

		self.enablePhysics(True)

		hitboxLeft = physical_data.get("hitboxLeft", 0)
		hitboxRight = physical_data.get("hitboxRight", 0)
		hitboxTop = physical_data.get("hitboxTop", 0)
		hitboxBottom = physical_data.get("hitboxBottom", 0)

		self.hitboxOffsetX = hitboxLeft
		self.hitboxOffsetY = hitboxTop

		self.hitboxWidth = self.size[0] - (hitboxLeft + hitboxRight)
		self.hitboxHeight = self.size[1] - (hitboxTop + hitboxBottom)

		self.vx = 0
		self.vy = 0
		self.on_ground = False

	def collisionX(self, block, ms):
		collisionRect = self.shiftedHitbox(roundAbsUp(self.vx * ms / 1000.), 0)
		collision = collisionRect.colliderect(block)

		if collision:
			if self.vx > 0:
				self.vx = 0
				self.x = block.left - self.hitbox().width - self.hitboxOffsetX
				return Direction.RIGHT
			elif self.vx < 0:
				self.vx = 0
				self.x = block.right - self.hitboxOffsetX
				return Direction.LEFT

		return Direction.NONE

	def collisionY(self, block, ms):
		collisionRect = self.shiftedHitbox(0, roundAbsUp(self.vy * ms / 1000.))
		collision = collisionRect.colliderect(block)

		if collision:
			if self.vy < 0:
				self.vy = 0
				self.y = block.bottom - self.hitboxOffsetY
				return Direction.UP
			elif self.vy > 0:
				self.vy = 0
				self.y = block.top - self.hitbox().height - self.hitboxOffsetY
				self.on_ground = True
				return Direction.DOWN
		return Direction.NONE

	def simulate_gravity(self, ms):
		self.vy = self.vy + config.gravity * (ms / 1000.)

		if self.vy >= config.max_vertical_speed / 1000.:
			self.vy = config.max_vertical_speed / 1000.

	def collideX(self, ms):

		# collide with map in x direction
		collisionTiles = self.layer.gamemap.tileRange(self.shiftedHitbox(roundAbsUp(self.vx * ms / 1000.), 0))

		for tile, tileRect in collisionTiles:
			if tile.collide:
				dirX = self.collisionX(tileRect, ms)
				if dirX != Direction.NONE:
					self.on_collision(dirX, None)

		# collide with entities in x direction
		collision_list = config.current_map.physicalEntities.copy()
		collision_list.remove(self)

		for block in collision_list:
			dirX = self.collisionX(block.hitbox(), ms)
			if dirX != Direction.NONE:
				self.on_collision(dirX, block)
				block.on_collision(dirX * -1, self)

	def collideY(self, ms):

		# collide with map in y direction
		collisionTiles = self.layer.gamemap.tileRange(self.shiftedHitbox(0, roundAbsUp(self.vy * ms / 1000.)))

		for tile, tileRect in reversed(collisionTiles):
			if tile.collide:
				dirY = self.collisionY(tileRect, ms)
				if dirY != Direction.NONE:
					self.on_collision(dirY, None)

		# collide with entities in y direction
		collision_list = config.current_map.physicalEntities.copy()
		collision_list.remove(self)

		for block in collision_list:
			dirX = self.collisionX(block.hitbox(), ms)
			dirY = self.collisionY(block.hitbox(), ms)
			if dirY != Direction.NONE:
				self.on_collision(dirY, block)
				block.on_collision(dirY * -1, self)

	def hitbox(self):
		x = int(self.x + self.hitboxOffsetX)
		y = int(self.y + self.hitboxOffsetY)
		return pygame.Rect(x, y, self.hitboxWidth, self.hitboxHeight)

	def shiftedHitbox(self, offsetX, offsetY):
		x = int(self.x + offsetX + self.hitboxOffsetX)
		y = int(self.y + offsetY + self.hitboxOffsetY)
		return pygame.Rect(x, y, self.hitboxWidth, self.hitboxHeight)

	def on_collision(self, direction, obj = None):
		pass
	
	def die(self):
		self.enablePhysics(False)
		super().die()

	def enablePhysics(self, enable = True):
		self.physics = enable
		if enable:
			self.layer.gamemap.physicalEntities.add(self)
		else:
			self.remove(self.layer.gamemap.physicalEntities)

	def update(self, ms):
		if(self.physics):
			self.on_ground = False
			self.simulate_gravity(ms)

			self.collideX(ms)
			self.x += ms / 1000.  * self.vx

			self.collideY(ms)
			self.y += ms / 1000.  * self.vy
		super().update(ms)
