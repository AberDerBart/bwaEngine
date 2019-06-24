import pygame
import json

from . import config

from .sprite import Orientation
from .game_object import GameObject, Direction

class MovingObject(GameObject):
	acc = 500
	speed = 100

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		#sound
		self.jump_sound = pygame.mixer.Sound('sound/jump.wav')
		self.channel = pygame.mixer.find_channel()
		if self.channel:
			self.channel.set_volume(.3)

		self.jumpTime = 0
		self.jumping = False

		self.idle()

	def run_left(self):
		self.targetSpeed = -self.speed
		self.orientation = Orientation.LEFT
		# TODO: make sprite check for its orientation on every frame
		self.updateSpritePosition()
		if self.sprite:
			self.sprite.setAnimation('run')

	def run_right(self):
		self.targetSpeed = self.speed
		self.orientation = Orientation.RIGHT
		# TODO: make sprite check for its orientation on every frame
		self.updateSpritePosition()
		if self.sprite:
			self.sprite.setAnimation('run')

	def jump(self, hold = True):
		if self.on_ground and hold:
			self.channel.play(self.jump_sound)
			self.jumping = True
			self.jumpTime = 0
		if not hold:
			self.jumping = False
	def idle(self):
		self.targetSpeed = 0
		if self.sprite:
			self.sprite.setAnimation('idle')

	def on_edge(self, direction):
		pass

	def die(self):
		self.targetSpeed = 0
		super().die()

	def update(self, ms, frameIndex):
		# handle horizontal movement
		if self.targetSpeed > self.vx:
			self.vx = min(self.vx + self.acc * ms / 1000., self.targetSpeed)
		elif self.targetSpeed < self.vx:
			self.vx = max(self.vx - self.acc * ms / 1000., self.targetSpeed)

		# handle jumping
		if self.jumpTime < 250:
			self.jumpTime += ms
			if self.jumping:
				# stay rising constantly, until the maximal jumptime has passed
				self.vy = -200
			else:
				# decellerate jump with twice the speed, im jump button was released
				if self.vy < 0:
					self.simulate_gravity(ms)

		# edge detection
		if self.on_ground and self.vx != 0:
			groundY = self.bottom
			
			if self.vx > 0:
				direction = Direction.RIGHT
				groundX = self.right
			else:
				direction = Direction.LEFT
				groundX = self.left

			nextTile = config.current_map.tileAt((groundX,groundY))
			
			if not nextTile or not nextTile.collides():
				self.on_edge(direction)

		super().update(ms, frameIndex)
