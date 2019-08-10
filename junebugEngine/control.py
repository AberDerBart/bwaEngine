import pygame

from .game_object import Direction
from . import keymap

class Control:
	keymap = {}
	entity = None
	def setEntity(entity):
		Control.keymap = keymap.keymaps.get(type(entity), {})
		Control.entity = entity
	def processEvent(event):
		if event.type in [pygame.KEYDOWN, pygame.KEYUP]:
			if event.key in Control.keymap:
				Control.keymap[event.key](Control.entity, event.type == pygame.KEYDOWN)

class PlayerControl:
	def __init__(self, char=None):
		self.char = char
		self.active = []

	def setCharacter(self, char):
		self.char = char
		self.active = []
	def right(self, pressed):
		if pressed:
			self.char.run_right()
		else:
			if PlayerControl.left in self.active:
				self.char.run_left()
			else:
				self.char.idle()
	def left(self, pressed):
		if pressed:
			self.char.run_left()
		else:
			if PlayerControl.right in self.active:
				self.char.run_right()
			else:
				self.char.idle()
	def jump(self, pressed):
		self.char.jump(pressed)
	def attack(self, pressed):
		if pressed:
			self.char.special()
	def switch(self, pressed):
		if pressed:
			self.char = self.char.switch()
