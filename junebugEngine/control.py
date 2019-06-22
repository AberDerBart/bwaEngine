import pygame

from .game_object import Direction

class PlayerControl:
	def __init__(self, keymap = {}, char=None):
		self.char = char
		self.keymap = keymap
		self.active = []

	def setCharacter(self, char):
		self.char = char
		self.active = []
	def processEvent(self, event):
		if self.char:
			if event.type == pygame.KEYUP:
				action = self.keymap.get(event.key)
				if action and action in self.active:
					self.active.remove(action)
					action(self, False)
			if event.type == pygame.KEYDOWN:
				action = self.keymap.get(event.key)
				if action:
					self.active.append(action)
					action(self, True)
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
