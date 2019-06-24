import pygame
import junebugEngine.config
from .game_map import EntityLayer

class Viewport:
	def __init__(self, size, map_, offset=(0,0), paddingTop = 0, paddingBottom = 0, paddingLeft = 0, paddingRight = 0):
		self.surf = pygame.Surface(size).convert()
		self.offsetx = offset[0]
		self.offsety = offset[1]

		self.map_ = map_

		if(self.map_.background):
			self.bg = pygame.transform.scale(self.map_.background, size)
		else:
			self.bg = pygame.Surface(size).convert()

		self.width = size[0]
		self.height = size[1]

		self.rect = pygame.Rect((- self.offsetx, - self.offsety),
                                (self.width, self.height))

		self.paddingTop = paddingTop
		self.paddingBottom = paddingBottom
		self.paddingLeft = paddingLeft
		self.paddingRight = paddingRight

		self.visibleEntities = pygame.sprite.Group()
		self.frameIndex = 0

		self.clear()

	def clear(self):
		self.surf.blit(self.bg, (0,0))

	def update(self,ms):
		# reset to background
		self.clear()
		# update the map
		self.map_.update(ms)

		self.frameIndex += 1

		# update physics for visible entities:
		for obj in self.map_.anchored:
			obj.update(ms, self.frameIndex)
		for obj in self.map_.anchored:
			obj.physicsX(ms)
		for obj in self.map_.anchored:
			obj.physicsY(ms)

		# update visible entities
		for layer in self.map_.layers:
			if type(layer) == EntityLayer:
				for sprite in layer.entities:
					if self.sprite_visible(sprite):
						sprite.update(ms)

		# adjust offset
		if self.map_.player:
			playerRect = self.map_.player.toPixel()
			if playerRect.left + self.offsetx < self.paddingLeft:
				self.offsetx = self.paddingLeft - playerRect.left
			elif playerRect.right + self.offsetx > self.width - self.paddingRight:
				self.offsetx = int(self.width - self.paddingRight - playerRect.right)

			if playerRect.top + self.offsety < self.paddingTop:
				self.offsety = int(self.paddingTop - playerRect.top)
			elif playerRect.bottom + self.offsety > self.height - self.paddingBottom:
				self.offsety = int(self.height - self.paddingBottom - playerRect.bottom)
			self.clipOffset()
		

		self.rect.top = - self.offsety
		self.rect.left = - self.offsetx
		self.rect.bottom = - self.offsety + self.height
		self.rect.right = - self.offsetx + self.width

		self.draw()



	def clipOffset(self):
		if self.map_:
			levelWidth = self.map_.pixelWidth()
			levelHeight = self.map_.pixelHeight()
			scrWidth = self.width
			scrHeight = self.height

			if self.offsetx < scrWidth - levelWidth:
				self.offsetx = scrWidth - levelWidth
			if self.offsetx > 0:
				self.offsetx = 0
			if self.offsety < scrHeight - levelHeight:
				self.offsety = scrHeight - levelHeight
			if self.offsety > 0:
				self.offsety = 0

	def draw(self):
		# draw next frame
		if(self.map_):
			self.map_.render(self.surf, (self.offsetx, self.offsety))

	def sprite_visible(self, sprite):
		return self.rect.colliderect(sprite.rect)

	def obj_visible(self, obj):
		if obj.typeName in ['berndman', 'wonderstevie', 'camera']:
			return True
		if not obj.sprite:
			return False
		return self.sprite_visible(obj.sprite)
