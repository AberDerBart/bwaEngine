import pygame
from .control import PlayerControl

"""DEFAULT KEYMAP"""
defaultKeymap = {
	pygame.K_LEFT: PlayerControl.left,
	pygame.K_RIGHT: PlayerControl.right,
	pygame.K_SPACE: PlayerControl.jump,
	pygame.K_LCTRL: PlayerControl.attack,
	pygame.K_UP: PlayerControl.switch
}

left_key = pygame.K_LEFT
right_key = pygame.K_RIGHT
jump_key = pygame.K_SPACE

right_attack_key = pygame.K_RCTRL
left_attack_key = pygame.K_LCTRL

change_hero_key = pygame.K_UP
