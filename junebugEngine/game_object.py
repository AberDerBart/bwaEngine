from pygame.rect import Rect
from .sprite import Orientation, Alignment
from . import config

PHYSICS_SCALE = 1024

class Direction(Orientation):
	NONE = 0
	UP = -1
	DOWN = 1

class GameObject(Rect):
	typeName = None
	gravity = False
	collides = False
	blocks = False

	def __init__(self, world = None, position = (0, 0), size = (0,0), align = Alignment.BOTTOMLEFT, **kwargs):
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

		self.world = world
		self.frameIndex = 0
		self.lastTruncPosition = self.truncate().topleft

		self.truncDx = 0
		self.truncDy = 0

		self.vx = 0
		self.vy = 0
		self.on_ground = False
	def resetPhysics(self):
		self.blocks = type(self).blocks
		self.gravity = type(self).gravity
		self.collides = type(self).collides

	def setSprite(self, sprite, spriteOffset = (0,0)):
		self.sprite = sprite
		self.spriteOffset = spriteOffset
		self.updateSpritePosition()

	def anchorTo(self, anchor):
		"""anchors the GameObject to another GameObject - any movement of the anchor is copied to the object"""
		# if we lose the anchor, keep it for the children
		if anchor == self.anchor:
			return

		if not anchor:
			for obj in self.anchored:
				obj.anchorTo(self.anchor)
		# exchange the anchor
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

	def collideRectX(self, other, dx, block = True):
		collisionRect = self.move(dx, 0)
		collision = collisionRect.colliderect(other)

		dirX = Direction.NONE

		if collision:
			if other.centerx > self.centerx:
				dirX = Direction.RIGHT
				if block:
					self.vx = 0
					dx = other.left - self.right 
			elif other.centerx < self.centerx:
				dirX = Direction.LEFT
				if block:
					self.vx = 0
					dx = other.right - self.left
		return dx, dirX
	
	def collideRectY(self, other, dy, block = True):
		collisionRect = self.move(0, dy)
		collision = collisionRect.colliderect(other)
		
		dirY = Direction.NONE
		
		if collision:
			if other.centery > self.centery:
				dirY = Direction.DOWN
				if block:
					self.vy = 0
					dy = other.top - self.bottom
			elif other.centery < self.centery:
				dirY = Direction.UP
				if block:
					self.vy = 0
					dy = other.bottom - self.top
		return dy, dirY

	def simulate_gravity(self, ms):
		self.vy = self.vy + config.gravity * (ms / 1000.)

		if self.vy >= config.max_vertical_speed / 1000.:
			self.vy = config.max_vertical_speed / 1000.

	def physicsX(self, ms):

		dx = self.absDx(self.vx * ms)

		# collide with map in x direction
		if not self.anchor:
			return 0
		collisionTiles = self.world.tileRange(self.move(dx, 0))

		for tile, tileRect in collisionTiles:
			if tile.collide:
				dx, dirX = self.collideRectX(tileRect, dx, self.collides)

				if dirX != Direction.NONE:
					self.on_collision(dirX, None)
					if not dx:
						return 0

		# collide with entities in x direction
		collision_list = self.collisionCandidates(self.union(self.move((dx, 0))))

		for block in collision_list:
			dx, dirX = self.collideRectX(block, dx, self.blocks and block.blocks and self.collides)
			if dirX != Direction.NONE:
				self.on_collision(dirX, block)
				block.on_collision(dirX * -1, self)
				if not dx:
					return 0
		
		return dx

	def physicsY(self, ms):

		dy = self.absDy(self.vy * ms)

		# collide with map in y direction
		if not self.anchor:
			return 0

		collisionTiles = self.world.tileRange(self.move(0, dy))

		for tile, tileRect in reversed(collisionTiles):
			if tile.collide:
				dy, dirY = self.collideRectY(tileRect, dy, self.collides)
				if dirY != Direction.NONE:
					self.on_collision(dirY, None)
					if not dy:
						return 0

		# collide with entities in y direction
		collision_list = self.collisionCandidates(self.union(self.move((0, dy))))

		for block in collision_list:
			dy, dirY = self.collideRectY(block, dy, self.blocks and block.blocks and self.collides)
			if dirY != Direction.NONE:
				self.on_collision(dirY, block)
				block.on_collision(dirY * -1, self)
				if not dy:
					return 0

		if not self.on_ground:
			self.anchorTo(self.world)

		return dy

	def on_collision(self, direction, obj = None):
		if direction == Direction.DOWN:
			if not obj:
				self.on_ground = True
				self.anchorTo(self.world)
			elif obj.blocks and self.blocks:
				self.on_ground = True
				self.anchorTo(obj)
		
	def boundingBox(self):
		return self.unionall(self.anchored)

	def absDx(self, dx = 0):
		if self.anchor:
			return self.anchor.absDx(dx) + self.anchor.truncDx 
		else:
			return dx

	def absDy(self, dy = 0):
		if self.anchor:
			return self.anchor.absDy(dy) + self.anchor.truncDy 
		else:
			return dy
		
	def update(self, ms, frameIndex):
		self.frameIndex = frameIndex

		self.on_ground = False
		if self.gravity:
			self.simulate_gravity(ms)
			
		self.x += self.physicsX(ms)
		self.y += self.physicsY(ms)

		self.updateSpritePosition()

		self.truncDx = self.truncate().x - self.lastTruncPosition[0]
		self.truncDy = self.truncate().y - self.lastTruncPosition[1]

		for obj in self.anchored:
			if obj.frameIndex != frameIndex:
				obj.update(ms, frameIndex)

		self.lastTruncPosition = self.truncate().topleft

	def die(self):
		self.anchorTo(None)
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

