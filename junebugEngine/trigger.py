import pygame
from .game_object import GameObject
from .tileset import EntityData

triggers = {"quit": pygame.quit}

class Trigger(GameObject):
    triggerDict = {"quit": pygame.quit}

    typeName = "trigger"
    collides = True

    def __init__(self, function = '', **kwargs):
        super().__init__(**kwargs)
        print('init trigger', function, kwargs)
        self.function = Trigger.triggerDict.get(function)
        self.functionName = function

    def on_collision(self, direction, other):
        super().on_collision(direction, other)
        if other == self.world.player:
            print("Triggering function '{}'".format(self.functionName))
            self.function()

EntityData.registerType(Trigger)
