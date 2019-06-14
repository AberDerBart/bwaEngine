from pygame.rect import Rect

PHYSICS_SCALE = 1024

class GameObject(Rect):
	def __init__(self, position, size = (0,0)):
		super().__init__(position, size)
		self.sprite = None
		self.spriteOffset = (0,0)
	def setSprite(self, sprite, spriteOffset = (0,0)):
		self.sprite = sprite
		self.spriteOffset = spriteOffset
		self.updateSpritePosition()
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
		self.sprite.x = self.toPixel().x + self.spriteOffset[0]
		self.sprite.y = self.toPixel().y + self.spriteOffset[1]
		self.sprite.setPosition((self.sprite.x, self.sprite.y))

