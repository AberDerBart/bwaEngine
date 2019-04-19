import pygame
import json
import operator
from sprite import AnimSprite, Orientation
import config
from enum import Enum
from util import relativePath

class Direction(Orientation):
	NONE = 0
	UP = -1
	DOWN = 1

class PhysicalObject(AnimSprite):
	typeName = None

	def __init__(self, json_sprite, physical_data, map_, initial_position):
		super().__init__(json_sprite, map_, initial_position)

		map_.physicalEntities.add(self)

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
		is_collisionX = False
		direction_list = []
		if self.vx > 0:
			right_rect = self.hitbox_rect.move(max(1,
                                self.vx * ms / 1000.), 0)
			right_collision = pygame.Rect.colliderect(right_rect, block.hitbox_rect)
			if right_collision:
				self.x = block.hitbox_rect.left - self.hitbox_rect.width - self.hitboxOffsetX
				#self.on_collision(Direction.RIGHT, block)
				#block.on_collision(Direction.LEFT, self)
				self.vx = 0
				is_collisionX = True
				direction_list.append(Direction.RIGHT)
		elif self.vx < 0:
			left_rect = self.hitbox_rect.move(min(-1,
                               self.vx * ms / 1000.), 0)
			left_collision = pygame.Rect.colliderect(left_rect, block.hitbox_rect)
			if left_collision:
				self.x = block.hitbox_rect.right - self.hitboxOffsetX
				#self.on_collision(Direction.LEFT, block)
				#block.on_collision(Direction.RIGHT, self)
				self.vx = 0
				is_collisionX = True
				direction_list.append(Direction.LEFT)
		return is_collisionX, direction_list

	def collisionY(self, block, ms):
		is_collisionY = False
		direction_list = []
		if self.vy < 0:
			top_rect = self.hitbox_rect.move(0, min(-1,
                              self.vy * ms / 1000.))
			top_collision = pygame.Rect.colliderect(top_rect, block.hitbox_rect)
			if top_collision:
				self.y = block.hitbox_rect.bottom - self.hitboxOffsetY
				#self.on_collision(Direction.UP, block)
				#block.on_collision(Direction.DOWN, self)
				self.vy = 0
				is_collisionY = True
				direction_list.append(Direction.UP)
		if self.vy > 0:
			bottom_rect = self.hitbox_rect.move(0, max(1,
                                 self.vy * ms / 1000.))
			bottom_collision = pygame.Rect.colliderect(bottom_rect, block.hitbox_rect)
			if bottom_collision:
				self.y = block.hitbox_rect.top - self.hitbox_rect.height - self.hitboxOffsetY
				#self.on_collision(Direction.DOWN, block)
				#block.on_collision(Direction.UP, self)
				self.on_ground = True
				self.vy = 0
				is_collisionY = True
				direction_list.append(Direction.DOWN)
		return is_collisionY, direction_list


	def simulate_collision(self, ms):
		collision_list = config.current_map.physicalEntities.copy()
		collision_list.remove(self)

		for block in collision_list:
			is_collisionX, dir_listX = self.collisionX(block, ms)
			self.hitbox_rect.left = self.x + self.hitboxOffsetX
			self.hitbox_rect.top = self.y + self.hitboxOffsetY
			is_collisionY, dir_listY = self.collisionY(block, ms)
			if is_collisionY:
				for direction in dir_listY:
					self.on_collision(direction, block)
					block.on_collision(direction * -1, self)
			elif is_collisionX:
				for direction in dir_listX:
					self.on_collision(direction, block)
					block.on_collision(direction * -1, self)

	def simulate_gravity(self, ms):
		self.vy = self.vy + config.gravity * (ms / 1000.)

		if self.vy >= config.max_vertical_speed / 1000.:
			self.vy = config.max_vertical_speed / 1000.

	def collide_with_map(self,ms):
		shiftX = self.vx * ms / 1000.
		shiftY = self.vy * ms / 1000.

		collisionTilesVertical = []
		if shiftY >= 0:
			collisionTilesVertical = self.map_.tileRange(self.shiftedHitbox(0, max(shiftY,1)))
		else:
			collisionTilesVertical = self.map_.tileRange(self.shiftedHitbox(0, shiftY))

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
		collisionTilesHorizontal = self.map_.tileRange(xHitbox)

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

	def update(self, ms):
		self.on_ground = False
		self.hitbox_rect.left = self.x + self.hitboxOffsetX
		self.hitbox_rect.top =self.y + self.hitboxOffsetY
		self.simulate_gravity(ms)
		self.collide_with_map(ms)
		self.simulate_collision(ms)
		self.x += ms / 1000.  * self.vx
		self.y += ms / 1000.  * self.vy
		super().update(ms)
