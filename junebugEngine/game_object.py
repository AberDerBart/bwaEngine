from pygame.rect import Rect
from .sprite import Orientation, Alignment

PHYSICS_SCALE = 1024

class GameObject(Rect):
	def __init__(self, position = (0, 0), size = (0,0), align = Alignment.BOTTOMLEFT, **kwargs):
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
		self.orientation = Orientation.RIGHT

		self.sprite = None
		self.spriteOffset = (0,0)
		
		self.anchor = None
		self.anchored = []

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

	def collisionCandidates(self, rect, _branch = None):
		candidates = []
		if _branch:
			for c in self.anchored:
				if c != _branch:
					candidates += [c]
					candidates += c.collisionCandidates(rect, self)
		if self.anchor is not None and _branch != self.anchor:
			candidates.append(self.anchor)
			candidates += self.anchor.collisionCandidates(rect, self)

		return candidates
		
	def boundingBox(self):
		return self.unionall(self.anchored)

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
			self.sprite.rect.topleft = self.toPixel().move(self.spriteOffset).topleft
			self.sprite.orientation = self.orientation

