import pygame
import json

from . import config

from .sprite import Orientation
from .physical_object import PhysicalObject, Direction

class MovingObject(PhysicalObject):
	acc = 500
	def __init__(self, json_sprite, physical_data, layer, initial_position, mirror_h, **kwargs):
		super().__init__(json_sprite, physical_data, layer, initial_position, mirror_h, **kwargs)

		self.speed = physical_data.get("baseSpeed", 0)

		#sound
		self.jump_sound = pygame.mixer.Sound('sound/jump.wav')
		self.channel = pygame.mixer.find_channel()
		self.channel.set_volume(.3)

		self.jumpTime = 0
		self.jumping = False

		self.idle()

	def run_left(self):
		self.targetSpeed = -self.speed
		self.orientation = Orientation.LEFT
		self.setAnimation('run')

	def run_right(self):
		self.targetSpeed = self.speed
		self.orientation = Orientation.RIGHT
		self.setAnimation('run')

	def jump(self, hold = True):
		if self.on_ground and hold:
			self.channel.play(self.jump_sound)
			self.jumping = True
			self.jumpTime = 0
		if not hold:
			self.jumping = False
	def idle(self):
		self.targetSpeed = 0
		self.setAnimation('idle')

	def on_edge(self, direction):
		pass

	def die(self):
		self.targetSpeed = 0
		super().die()

	def update(self,ms):
		#self.vx = self.targetSpeed
		if self.targetSpeed > self.vx:
			self.vx = min(self.vx + self.acc * ms / 1000., self.targetSpeed)
		elif self.targetSpeed < self.vx:
			self.vx = max(self.vx - self.acc * ms / 1000., self.targetSpeed)


		if self.jumpTime < 250:
			self.jumpTime += ms
			if self.jumping:
				# stay rising constantly, until the maximal jumptime has passed
				self.vy = -200
			else:
				# decellerate jump with twice the speed, im jump button was released
				if self.vy < 0:
					self.simulate_gravity(ms)

		super().update(ms)
		if self.on_ground and self.vx != 0:
			groundY = self.y + self.hitboxOffsetY + self.hitboxHeight
			
			if self.vx > 0:
				direction = Direction.RIGHT
				groundX = self.x + self.hitboxOffsetX + self.hitboxWidth
			else:
				direction = Direction.LEFT
				groundX = self.x + self.hitboxOffsetX

			nextTile = config.current_map.tileAt((groundX,groundY))
			
			if not nextTile or not nextTile.collides():
				self.on_edge(direction)

