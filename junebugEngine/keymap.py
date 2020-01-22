import pygame
from .control import PlayerControl
from .menu import Cursor
from .camera import Camera

_defaultKeymapCursor = {
    pygame.K_LEFT: Cursor.goLeft,
    pygame.K_RIGHT: Cursor.goRight,
    pygame.K_UP: Cursor.goUp,
    pygame.K_DOWN: Cursor.goDown,
    pygame.K_RETURN: Cursor.select,
    pygame.K_ESCAPE: Cursor.quit
}

_defaultKeymapPlayerControl = {
    pygame.K_LEFT: PlayerControl.left,
    pygame.K_RIGHT: PlayerControl.right,
    pygame.K_SPACE: PlayerControl.jump,
    pygame.K_LCTRL: PlayerControl.attack,
    pygame.K_UP: PlayerControl.switch,
    pygame.K_ESCAPE: PlayerControl.quit
}

_defaultKeymapCamera = {
    pygame.K_SPACE: Camera.skip,
    pygame.K_ESCAPE: Camera.quit
}

_defaultKeymaps = {
    Cursor: _defaultKeymapCursor,
    PlayerControl: _defaultKeymapPlayerControl,
    Camera: _defaultKeymapCamera
}
