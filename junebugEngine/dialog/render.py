"""renders a dialog to a pygame surface"""
import pygame
from .types import Dialog

pygame.font.init()

padding = 10
font = pygame.font.Font(pygame.font.get_default_font(), 20)

def render(surface: pygame.surface.Surface, dialog: Dialog, progress: int) -> int:
    """renders the given dialog to the given surface"""
    sentence = dialog.sentences[progress]
    portrait = sentence.speaker.portrait
    pos_y = surface.get_height() - portrait.get_height()

    rect = pygame.Rect(0, pos_y, surface.get_width(), portrait.get_height())

    text_surf = font.render(sentence.text, False, sentence.speaker.color)

    # TODO: make color adjustable
    pygame.draw.rect(surface, pygame.color.Color(0, 0, 0), rect)
    surface.blit(portrait, (0, pos_y))
    surface.blit(text_surf, (portrait.get_width() + padding, pos_y + padding))
