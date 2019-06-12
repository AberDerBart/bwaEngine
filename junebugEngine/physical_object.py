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

	def collideRect(self, block, ms, dx=0, dy=0):
		collisionRect = self.shiftedHitbox(roundAbsUp(dx), roundAbsUp(dy))
		collision = collisionRect.colliderect(block)

		if collision:
			if dx > 0:
				self.vx = 0
				self.x = block.left - self.hitbox().width - self.hitboxOffsetX
				return Direction.RIGHT
			elif dx < 0:
				self.vx = 0
				self.x = block.right - self.hitboxOffsetX
				return Direction.LEFT
			elif dy < 0:
				self.vy = 0
				self.y = block.bottom - self.hitboxOffsetY
				return Direction.UP
			elif dy > 0:
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

		dx = self.vx * ms / 1000.

		for tile, tileRect in collisionTiles:
			if tile.collide:
				dirX = self.collideRect(tileRect, ms, dx=dx)
				if dirX != Direction.NONE:
					self.on_collision(dirX, None)
					dx = self.vx * ms / 1000.

		# collide with entities in x direction
		collision_list = config.current_map.physicalEntities.copy()
		collision_list.remove(self)

		for block in collision_list:
			dirX = self.collideRect(block.hitbox(), ms, dx=dx)
			if dirX != Direction.NONE:
				self.on_collision(dirX, block)
				block.on_collision(dirX * -1, self)
				dx = self.vx * ms / 1000.

	def collideY(self, ms):

		# collide with map in y direction
		collisionTiles = self.layer.gamemap.tileRange(self.shiftedHitbox(0, roundAbsUp(self.vy * ms / 1000.)))

		dy = self.vy * ms / 1000.

		for tile, tileRect in reversed(collisionTiles):
			if tile.collide:
				dirY = self.collideRect(tileRect, ms, dy=dy)
				if dirY != Direction.NONE:
					self.on_collision(dirY, None)
					dy = self.vy * ms / 1000.

		# collide with entities in y direction
		collision_list = config.current_map.physicalEntities.copy()
		collision_list.remove(self)

		for block in collision_list:
			dirY = self.collideRect(block.hitbox(), ms, dy=dy)
			if dirY != Direction.NONE:
				self.on_collision(dirY, block)
				block.on_collision(dirY * -1, self)
				dy = self.vy * ms / 1000.

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
