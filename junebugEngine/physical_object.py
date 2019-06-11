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

		self.hitbox_rect = pygame.Rect(self.x + self.hitboxOffsetX,
                                  self.y + self.hitboxOffsetY,
                                  self.hitboxWidth,
                                  self.hitboxHeight)

		self.vx = 0
		self.vy = 0
		self.on_ground = False

	def collisionX(self, block, ms):
		collisionRect = self.shiftedHitbox(roundAbsUp(self.vx * ms / 1000.), 0)
		collision = collisionRect.colliderect(block.hitbox())

		if collision:
			if self.vx > 0:
				self.vx = 0
				self.x = block.hitbox().left - self.hitbox().width - self.hitboxOffsetX
				return Direction.RIGHT
			elif self.vx < 0:
				self.vx = 0
				self.x = block.hitbox().right - self.hitboxOffsetX
				return Direction.LEFT

		return Direction.NONE

	def collisionY(self, block, ms):
		collisionRect = self.shiftedHitbox(0, roundAbsUp(self.vy * ms / 1000.))
		collision = collisionRect.colliderect(block.hitbox())

		if collision:
			if self.vy < 0:
				self.vy = 0
				self.y = block.hitbox_rect.bottom - self.hitboxOffsetY
				return Direction.UP
			elif self.vy > 0:
				self.vy = 0
				self.y = block.hitbox_rect.top - self.hitbox_rect.height - self.hitboxOffsetY
				self.on_ground = True
				return Direction.DOWN
		return Direction.NONE


	def simulate_collision(self, ms):
		collision_list = config.current_map.physicalEntities.copy()
		collision_list.remove(self)

		for block in collision_list:
			dirX = self.collisionX(block, ms)
			dirY = self.collisionY(block, ms)
			if dirY != Direction.NONE:
				self.on_collision(dirY, block)
				block.on_collision(dirY * -1, self)
			if dirX != Direction.NONE:
				self.on_collision(dirX, block)
				block.on_collision(dirX * -1, self)

	def simulate_gravity(self, ms):
		self.vy = self.vy + config.gravity * (ms / 1000.)

		if self.vy >= config.max_vertical_speed / 1000.:
			self.vy = config.max_vertical_speed / 1000.

	def collide_with_map(self,ms):
		shiftX = self.vx * ms / 1000.
		shiftY = self.vy * ms / 1000.

		collisionTilesVertical = []
		if shiftY >= 0:
			collisionTilesVertical = self.layer.gamemap.tileRange(self.shiftedHitbox(0, max(shiftY,1)))
		else:
			collisionTilesVertical = self.layer.gamemap.tileRange(self.shiftedHitbox(0, shiftY))

		for tile, tileRect in reversed(collisionTilesVertical):
			if tile.collide:
				if shiftY > 0:
					self.y = tileRect.top - self.hitboxHeight - self.hitboxOffsetY
					self.on_ground=True
					self.on_collision(Direction.DOWN, None)
				else:
					self.y = tileRect.bottom
					self.on_collision(Direction.UP, None)
				self.vy = 0

		shiftY = self.vy * ms / 1000.
		xHitbox = self.shiftedHitbox(shiftX, shiftY)
		collisionTilesHorizontal = self.layer.gamemap.tileRange(xHitbox)

		for tile, tileRect in collisionTilesHorizontal:
			if tile.collide:
				if tileRect.left >= xHitbox.left:
					self.on_collision(Direction.RIGHT, None)
				else:
					self.on_collision(Direction.LEFT, None)
				self.vx = 0

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
			self.hitbox_rect.left = self.x + self.hitboxOffsetX
			self.hitbox_rect.top =self.y + self.hitboxOffsetY
			self.simulate_gravity(ms)
			self.collide_with_map(ms)
			self.simulate_collision(ms)
			self.x += ms / 1000.  * self.vx
			self.y += ms / 1000.  * self.vy
		super().update(ms)
