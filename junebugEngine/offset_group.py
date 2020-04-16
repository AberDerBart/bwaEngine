import pygame
from .sprite import AnimSprite


class OffsetGroup(pygame.sprite.Group):
    def draw(self, surface, offset=(0, 0)):

        sprites = self.sprites()

        for spr in sprites:
            surface.blit(spr.image, spr.rect.move(*offset))
            if isinstance(spr, AnimSprite):
                for particle in spr.particles:
                    pygame.draw.circle(surface,
                                       (255, 255, 255),
                                       particle[0],
                                       particle[2])
        self.lostsprites = []

    def clear(self, surface, bgd, offset=(0, 0)):

        if callable(bgd):
            for r in self.lostsprites:
                bgd(surface, r)
            for r in self.spritedict.values():
                if r:
                    bgd(surface, r)
        else:
            surface_blit = surface.blit
            for r in self.lostsprites:
                surface_blit(bgd, r, r)
            for r in self.spritedict.values():
                if r:
                    surface_blit(bgd, r, r)
