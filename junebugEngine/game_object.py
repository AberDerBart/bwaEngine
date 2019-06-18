from pygame.rect import Rect
from .sprite import Orientation

PHYSICS_SCALE = 1024

class Alignment:
	CENTER = 0
	LEFT = 1
	RIGHT = 2
	TOP = 4
	BOTTOM = 8
	TOPLEFT = 5
	TOPRIGHT = 6
	BOTTOMLEFT = 9
	BOTTOMRIGHT = 10

class GameObject(Rect):
	def __init__(self, position, size = (0,0), align = Alignment.BOTTOMLEFT):
		if align & Alignment.LEFT:
			x = position[0]
		elif align & Alignment.RIGHT:
			x = position[0] - size[0]
		else:
			x = position[0] - size[0] / 2

		if align & Alignment.TOP:
			y = position[1]
		elif align & Alignment.BOTTOM:
			y = position[1] - size[1]
		else:
			y = position[1] - size[1] / 2
		
		super().__init__((x, y), size)
		self.sprite = None
		self.spriteOffset = (0,0)
		self.anchor = None
		self.orientation = Orientation.RIGHT

	def setSprite(self, sprite, spriteOffset = (0,0)):
		self.sprite = sprite
		self.spriteOffset = spriteOffset
		self.updateSpritePosition()
	def anchorTo(self, anchor):
		if self.anchor:
			self.anchor.anchored.remove(self)
		self.anchor = anchor
		if anchor:
			anchor.anchored.append(self)

	def update(self, ms):
		self.updateSpritePosition()

	def die(self):
		if self.sprite:
			self.sprite.die()

	def truncate(self):
		x = self.x - self.x % PHYSICS_SCALE
		y = self.y - self.y % PHYSICS_SCALE
		w = self.w - self.w % PHYSICS_SCALE
		h = self.h - self.h % PHYSICS_SCALE
		return Rect(x, y, w, h)
	def toPixel(self):
		x = self.x // PHYSICS_SCALE
		y = self.y // PHYSICS_SCALE
		w = self.w // PHYSICS_SCALE
		h = self.h // PHYSICS_SCALE
		return Rect(x, y, w, h)
	def updateSpritePosition(self):
		if self.sprite:
			x = self.toPixel().x + self.spriteOffset[0]
			y = self.toPixel().y + self.spriteOffset[1]
			self.sprite.setPosition((x, y))
			self.sprite.orientation = self.orientation

