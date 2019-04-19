import pygame
import config
from util import convertCoords

class RenderedText(pygame.sprite.Sprite):
	typeName = "text"
	def __init__(self, pos, data):
		super().__init__()

		color = pygame.Color(data.get("color","#000000"))
		self.text = data.get("text","")
		fontPath = config.fonts.get(data.get("fontfamily"))
		size = int(convertCoords(data.get("pixelsize", 16)))

		font = pygame.font.Font(fontPath, size)

		self.image = font.render(self.text,False,color)
		self.rect = pygame.Rect(pos, self.image.get_size())
		self.x = pos[0]
		self.y = pos[1]
	def setOffset(self,offset):
		x = self.x + offset[0]
		y = self.y + offset[1]
		self.rect = pygame.Rect((x,y), self.image.get_size())

	def on_screen_enter(self):
		pass

	def on_screen_exit(self):
		pass
