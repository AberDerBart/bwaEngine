import pygame
from .moving_object import MovingObject
from .physical_object import Direction
from .text import RenderedText

class Hero(MovingObject):
	def __init__(self, json_sprite, physical_data, layer, position):
		super().__init__(json_sprite, physical_data, layer, position)

		self.die_sound = pygame.mixer.Sound('sound/game_over.wav')
		self.channel = pygame.mixer.find_channel()
		self.num_beers = 0 ### :-(
		self.font_render_dict = {"color":"#FFFFFF",
                                 "fontfamily":"Lady Radical 2",
                                 "text":"#Beer: 0"}
		self.beer_counter = RenderedText((0, 0), self.font_render_dict)
		self.partner = None

	def update_hud(self):
		self.font_render_dict['text'] = "#Beer: " + str(self.num_beers)
		self.beer_counter = RenderedText((0, 0), self.font_render_dict)

	def die(self):
		self.channel.play(self.die_sound)
		self.num_beers = 0
		self.update_hud()
		super().die()

	def switch(self):
		if self.partner:
			super().die()
			self.layer.entities.add(self.partner)
			self.layer.gamemap.physicalEntities.add(self.partner)
			self.layer.gamemap.player = self.partner
			self.partner.x = self.x
			self.partner.y = self.y
			return self.partner
		return self

	def special(self):
		pass

	def on_collision(self, direction, obj):
		super().on_collision(direction, obj)
		if obj is not None and obj.typeName in ['beer']:
			self.num_beers += 1
			obj.die()
			self.font_render_dict['text'] = "#Beer: " + str(self.num_beers)
			self.beer_counter = RenderedText((0, 0), self.font_render_dict)
