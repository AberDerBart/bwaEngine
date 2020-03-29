from .game_object import GameObject
from .game import setSprite
from .tileset import EntityData
from .sprite import AnimSprite
from .trigger import triggers
from . import config


class Cursor(GameObject):
    typeName = "cursor"

    def __init__(self, sprite='', selected='', **kwargs):
        super().__init__(**kwargs)

        spr = AnimSprite(sprite)
        setSprite(self, spr, (-spr.rect.width/2, -spr.rect.height/2))
        self.goto = selected
        self.selected = None

    def update(self, ms, frameIndex):
        super().update(ms, frameIndex)
        if self.goto:
            self.selected = self.world.getEntity(self.goto)
            self.topleft = self.selected.topleft
            self.goto = ''

    def goLeft(self, press=True):
        if press and self.selected:
            self.goto = self.selected.leftOption

    def goRight(self, press=True):
        if press and self.selected:
            self.goto = self.selected.rightOption

    def goUp(self, press=True):
        if press and self.selected:
            self.goto = self.selected.upOption

    def goDown(self, press=True):
        if press and self.selected:
            self.goto = self.selected.downOption

    def select(self, press=True):
        if press and self.selected:
            self.selected.trigger()

    def quit(self, pressed):
        if pressed:
            config.running = False


EntityData.registerType(Cursor)


class MenuOption(GameObject):
    typeName = "menu"

    def __init__(self, left='', right='', up='',
                 down='', function='', **kwargs):
        super().__init__(**kwargs)
        self.leftOption = left
        self.rightOption = right
        self.upOption = up
        self.downOption = down
        self.function = function

    def trigger(self):
        if self.function in triggers:
            triggers[self.function]()


EntityData.registerType(MenuOption)
