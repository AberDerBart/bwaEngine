from pygame.rect import Rect
from .sprite import Orientation, Alignment
from .physics import PHYSICS_SCALE
from . import config


class GameObject():
    gravity = False
    collides = False
    blocks = False

    def __init__(self, world=None, position=(0, 0), size=(0, 0),
                 align=Alignment.BOTTOMLEFT, mirror_h=False, **kwargs):
        size = (size[0] * PHYSICS_SCALE,
                size[1] * PHYSICS_SCALE)
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

        self.rect = Rect((x, y), size)
        self.orientation = Orientation.LEFT if mirror_h else Orientation.RIGHT

        self.sprite = None
        self.spriteOffset = (0, 0)

        self.anchor = None
        self.anchored = []

        self.world = world
        self.frameIndex = 0

        self.truncDx = 0
        self.truncDy = 0

        self.vx = 0
        self.vy = 0
        self.on_ground = False

        self.chunks = []

        self.properties = kwargs

    def __bool__(self):
        return True
