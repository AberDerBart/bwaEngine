import pygame
import config
import json

from sprite import Orientation
from physical_object import PhysicalObject, Direction

class MovingObject(PhysicalObject):
	def __init__(self, json_sprite, physical_data, map_, initial_position):
		super().__init__(json_sprite, physical_data, map_, initial_position)

		self.speed = physical_data.get("baseSpeed", 0)

		#sound
		self.jump_sound = pygame.mixer.Sound('sound/jump.wav')
		self.channel = pygame.mixer.find_channel()
		self.channel.set_volume(.3)

		self.idle()

	def run_left(self):
		self.movement = -1
		self.orientation = Orientation.LEFT
		self.setAnimation('run')

	def run_right(self):
		self.movement = 1
		self.orientation = Orientation.RIGHT
		self.setAnimation('run')

	def jump(self):
		if self.on_ground:
			self.channel.play(self.jump_sound)
			self.vy = -min(270,config.max_vertical_speed)
	def idle(self):
		self.movement = 0
		self.setAnimation('idle')

	def on_edge(self, direction):
		pass

	def update(self,ms):
		self.vx = self.movement * self.speed
		super().update(ms)
		if self.on_ground and config.current_map and self.movement != 0:
			groundY = self.y + self.hitboxOffsetY + self.hitboxHeight
			
			if self.movement > 0:
				direction = Direction.RIGHT
				groundX = self.x + self.hitboxOffsetX + self.hitboxWidth
			elif self.movement < 0:
				direction = Direction.LEFT
				groundX = self.x + self.hitboxOffsetX

			nextTile = config.current_map.tileAt((groundX,groundY))
			
			if not nextTile or not nextTile.collides():
				self.on_edge(direction)

