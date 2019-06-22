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

	def __init__(self, world = None, position = (0, 0), size = (0,0), align = Alignment.BOTTOMLEFT, collides = False, collideable = False, **kwargs):
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

		self.physics = collides or collideable

	def setSprite(self, sprite, spriteOffset = (0,0)):
		self.sprite = sprite
		self.spriteOffset = spriteOffset
		self.updateSpritePosition()

	def anchorTo(self, anchor):
		print(self.typeName, 'anchorTo', anchor.typeName if anchor else anchor)
		print(self.vx, self.vy)
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

	def collideRectX(self, block, dx):
		collisionRect = self.move(dx, 0)
		collision = collisionRect.colliderect(block)

		dirX = Direction.NONE

		if collision:
			if dx > 0:
				self.vx = 0
				dx = block.left - self.right 
				dirX = Direction.RIGHT
			elif dx < 0:
				self.vx = 0
				dx = block.right - self.left
				dirX = Direction.LEFT
		return dx, dirX
	
	def collideRectY(self, block, dy):
		collisionRect = self.move(0, dy)
		collision = collisionRect.colliderect(block)
		
		dirY = Direction.NONE
		
		if collision:
			if dy > 0:
				self.vy = 0
				dy = block.top - self.bottom
				self.on_ground = True
				dirY = Direction.DOWN
			elif dy < 0:
				self.vy = 0
				dy = block.bottom - self.top
				dirY = Direction.UP
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
				dx, dirX = self.collideRectX(tileRect, dx)
				if dirX != Direction.NONE:
					self.on_collision(dirX, None)
					if not dx:
						return 0

		# collide with entities in x direction
		collision_list = self.collisionCandidates(self.union(self.move((dx, 0))))

		for block in collision_list:
			dx, dirX = self.collideRectX(block, dx)
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
				dy, dirY = self.collideRectY(tileRect, dy)
				if dirY == Direction.DOWN and self.anchor != self.world:
					self.anchorTo(self.world)
				if dirY != Direction.NONE:
					self.on_collision(dirY, None)
					if not dy:
						return 0

		# collide with entities in y direction
		collision_list = self.collisionCandidates(self.union(self.move((0, dy))))

		for block in collision_list:
			dy, dirY = self.collideRectY(block, dy)
			if dirY == Direction.DOWN:
				if self.anchor != block:
					self.anchorTo(block)
			if dirY != Direction.NONE:
				self.on_collision(dirY, block)
				block.on_collision(dirY * -1, self)
				if not dy:
					return 0

		if not self.on_ground and self.anchor != self.world:
			self.anchorTo(self.world)

		return dy

	def on_collision(self, direction, obj = None):
		pass
		
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

		if(self.physics):
			self.on_ground = False
			self.simulate_gravity(ms)
			
			self.x += self.physicsX(ms)
			self.y += self.physicsY(ms)
		else:
			self.x += self.absDx()
			self.y += self.absDy()

		self.updateSpritePosition()

		self.truncDx = self.truncate().x - self.lastTruncPosition[0]
		self.truncDy = self.truncate().y - self.lastTruncPosition[1]

		for obj in self.anchored:
			if obj.frameIndex != frameIndex:
				obj.update(ms, frameIndex)

		self.lastTruncPosition = self.truncate().topleft

	def die(self):
		print(self.typeName, 'die')
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

