import pygame
from .game_object import GameObject
from .tileset import EntityData
from .map_parser import MapParser
from .control import Control

triggers = {"quit": Control.quit}

class Trigger(GameObject):
    typeName = "trigger"
    collides = True

    def __init__(self, function='', dialog_name='', initial_step='', **kwargs):
        super().__init__(**kwargs)
        self.function = triggers.get(function)
        self.functionName = function
        self.dialogName = dialog_name
        self.initialStep = initial_step

    def on_collision(self, direction, other):
        super().on_collision(direction, other)
        if other == self.world.player:
            print("Triggering function '{}'".format(self.functionName))
            if self.functionName in ['start_rain', 'open_dialog']:
                self.function(self)
            else:
                self.function()

EntityData.registerType(Trigger)

class Goal(GameObject):
    typeName = "goal"
    collides = True

    def __init__(self, nextmap = '', **kwargs):
        super().__init__(**kwargs)
        self.nextMap = nextmap

    def switchLevel(self):
        viewports = set(self.world.viewports)

        if viewports:
            newMap = MapParser.parse(self.nextMap)
            Control.setEntity(newMap.player)
            for viewport in viewports:
                viewport.setMap(newMap)

    def on_collision(self, direction, other):
        super().on_collision(direction, other)
        if other == self.world.player:
            print("Reached Goal, transitioning to '{}'"
              .format(self.nextMap))
            self.switchLevel()

EntityData.registerType(Goal)
