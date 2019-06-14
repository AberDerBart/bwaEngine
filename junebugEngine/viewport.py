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

		self.clear()

	def clear(self):
		self.surf.blit(self.bg, (0,0))

	def update(self,ms):
		# reset to background
		self.clear()
		# update the map
		self.map_.update(ms)

		# update visible entities
		for layer in self.map_.layers:
			if type(layer) == EntityLayer:
				for entity in layer.entities:
					if self.is_visible(entity):
						entity.update(ms)
						if entity not in self.visibleEntities:
							entity.on_screen_enter()
							self.visibleEntities.add(entity)
					else:
						if entity in self.visibleEntities:
							entity.on_screen_exit()
							self.visibleEntities.remove(entity)

		# adjust offset
		if self.map_.player:
			if self.map_.player.sprite.rect.left + self.offsetx < self.paddingLeft:
				self.offsetx = self.paddingLeft - int(self.map_.player.x)
			elif self.map_.player.sprite.rect.right + self.offsetx > self.width - self.paddingRight:
				self.offsetx = int(self.width - self.paddingRight - int(self.map_.player.x) - self.map_.player.size[0])

			if self.map_.player.sprite.rect.top + self.offsety < self.paddingTop:
				self.offsety = int(self.paddingTop - self.map_.player.y)
			elif self.map_.player.sprite.rect.bottom + self.offsety > self.height - self.paddingBottom:
				self.offsety = int(self.height - self.paddingBottom - self.map_.player.y - self.map_.player.size[1])
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

	def is_visible(self, entity):
		visibility = False
		if entity.typeName in ['berndman', 'wonderstevie', 'camera']:
			visibility = True
		if self.rect.colliderect(entity.rect):
			visibility = True
		return visibility

