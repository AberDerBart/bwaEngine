import pygame
from .game_object import GameObject, PHYSICS_SCALE

class Camera(GameObject):
	typeName = "camera"

	def __init__(self, layer, path, timePerPoint, **kwargs):
		# TODO: make gameobject with no size not be falsy
		super().__init__(path[0], (PHYSICS_SCALE, PHYSICS_SCALE,), **kwargs)

		self.timePerPoint = int(timePerPoint * 1000)
		self.time = 0
		self.path = path

	def update(self, ms):
		self.time = self.time + ms

		pointProgress = self.time / self.timePerPoint
		lastPoint = int(self.time / self.timePerPoint)
		nextPoint = lastPoint + 1


		offset = pointProgress - lastPoint

		if nextPoint < len(self.path):
			self.x = self.path[lastPoint][0] * (1 - offset) + self.path[nextPoint][0] * offset
			self.y = self.path[lastPoint][1] * (1 - offset) + self.path[nextPoint][1] * offset
		else:
			self.x = self.path[-1][0]
			self.y = self.path[-1][1]

		super().update(ms)


