"""renders a dialog to a pygame surface"""
import pygame
from .types import Dialog

pygame.font.init()

padding = 15
font = pygame.font.Font(pygame.font.get_default_font(), 15)

def render(surface: pygame.surface.Surface, dialog: Dialog, progress: int) -> int:
    """renders the given dialog to the given surface"""
    portrait_border = pygame.image.load('art/portraits/portrait_border.png')
    sentence_border = pygame.image.load('art/portraits/sentence_border.png')
    sentence = dialog.sentences[progress]
    portrait = sentence.speaker.portrait
    pos_y = surface.get_height() - portrait.get_height()

    rect = pygame.Rect(0, pos_y, surface.get_width(), portrait.get_height())

    text_surf = font.render(sentence.text, False, sentence.speaker.color)
    portrait_border.set_colorkey((255, 0, 255))
    sentence_border.set_colorkey((255, 0, 255))

    # TODO: make color adjustable
    pygame.draw.rect(surface, pygame.color.Color(10, 10, 10), rect)
    surface.blit(portrait, (0, pos_y))
    surface.blit(portrait_border, (0, pos_y))
    surface.blit(text_surf, (portrait.get_width() + padding, pos_y + padding))
    surface.blit(sentence_border, (portrait.get_width(), pos_y))
