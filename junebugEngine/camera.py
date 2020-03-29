from .game_object import GameObject
from .map_parser import MapParser
from .tileset import EntityData
from . import config, game

class Camera(GameObject):
    """A camera object for making "video" sequences

    The camera follows a path."""


    typeName = "camera"
    collides = True

    def __init__(self, polyline=[], timePerPoint=0, skipToMap=None, **kwargs):
        """Initializes the camera."""

        print(skipToMap)
        print(kwargs)
        kwargs['size'] = (1,1)
        super().__init__(**kwargs)

        self.timePerPoint = int(timePerPoint * 1000)
        self.time = 0
        self.path = polyline
        self.skipToMap = skipToMap

    def skip(self, pressed=True):
        """skips the sequence and continues to the next GameMap [self.skipToMap]"""

        if pressed and self.skipToMap:
            print('skip')
            self.world.switchToMap(MapParser.parse(self.skipToMap))
        else:
            print(pressed, self.skipToMap)

    def update(self, ms, frameIndex):
        """Advance the Camera along the path"""

        self.time = self.time + ms

        pointProgress = self.time / self.timePerPoint
        lastPoint = int(self.time / self.timePerPoint)
        nextPoint = lastPoint + 1

        offset = pointProgress - lastPoint

        if nextPoint < len(self.path):
            self.x = self.path[lastPoint][0] * (1 - offset) \
                + self.path[nextPoint][0] * offset
            self.y = self.path[lastPoint][1] * (1 - offset) \
                + self.path[nextPoint][1] * offset
        else:
            self.x = self.path[-1][0]
            self.y = self.path[-1][1]

        game.update(self, ms, frameIndex)

    def quit(self, pressed):
        """Closes the game."""

        if pressed:
            config.running = False

EntityData.registerType(Camera)
