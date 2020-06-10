import pygame
from .game_map import EntityLayer
from .game_object import PHYSICS_SCALE
from .dialog import parse as dialog_parse
from .dialog import render as dialog_render
from .dialogplayer import DialogPlayer
from .control import Control


class Viewport:
    def __init__(self, size, map_, offset=(0, 0), paddingTop=0,
                 paddingBottom=0, paddingLeft=0, paddingRight=0):
        self.surf = pygame.Surface(size).convert()
        self.offsetx = offset[0]
        self.offsety = offset[1]

        self.width = size[0]
        self.height = size[1]

        self.map_ = None
        self.setMap(map_)

        self.dialog = None
        self.player_queue = []
        self.dialog_player = None

        self.rect = pygame.Rect((- self.offsetx, - self.offsety),
                                (self.width, self.height))

        self.paddingTop = paddingTop
        self.paddingBottom = paddingBottom
        self.paddingLeft = paddingLeft
        self.paddingRight = paddingRight

        self.frameIndex = 0

        self.clear()

    def setMap(self, map_):

        self.offsetx = 0
        self.offsety = 0

        if self.map_:
            self.map_.viewports.discard(self)
        self.map_ = map_
        self.map_.viewports.add(self)

        if self.map_.player:
            self.paddingTop = \
              self.map_.player.properties.get('marginTop', 0) *\
              (self.height - self.map_.player.height/ PHYSICS_SCALE)
            self.paddingBottom = \
              self.map_.player.properties.get('marginBottom', 0) *\
              (self.height - self.map_.player.height / PHYSICS_SCALE)
            self.paddingLeft = \
              self.map_.player.properties.get('marginLeft', 0) *\
              (self.width - self.map_.player.width / PHYSICS_SCALE)
            self.paddingRight = \
              self.map_.player.properties.get('marginRight', 0) *\
              (self.width - self.map_.player.width/ PHYSICS_SCALE)

        if(self.map_.background):
            self.bg = pygame.transform.scale(self.map_.background, (self.width,
              self.height))
        else:
            self.bg = pygame.Surface((self.width, self.height)).convert()

    def clear(self):
        self.surf.blit(self.bg, (0, 0))

    def set_dialog(self, dialog_trigger):
        self.dialog_trigger = dialog_trigger
        dialog_filepath = ('levels/dialogs/' +
                           str(self.dialog_trigger.dialogName) + '.json')
        self.dialog = dialog_parse(dialog_filepath)
        self.next_step = int(self.dialog_trigger.initialStep)
        self.dialog_player = DialogPlayer(viewport=self)
        self.player_queue.append(self.map_.player)
        Control.setEntity(self.dialog_player)
        self.map_.player = self.dialog_player
        return True

    def update(self, ms):
        # update the map
        self.map_.update(ms)
        if self.dialog:
            if self.next_step < len(self.dialog.sentences):
                dialog_render(surface=self.surf,
                              dialog=self.dialog,
                              progress=self.next_step)
            else:
                self.dialog = None
                self.dialog_player = None
                self.map_.player = self.player_queue.pop()
                self.map_.player.idle()
                Control.setEntity(self.map_.player)
                self.next_step = 0
            return
        # reset to background
        self.clear()

        self.frameIndex += 1

        # update physics for visible entities:
        for obj in self.map_.anchored:
            if self.obj_visible(obj):
                obj.update(ms, self.frameIndex)
        for obj in self.map_.anchored:
            if self.obj_visible(obj):
                obj.physicsX(ms)
        for obj in self.map_.anchored:
            if self.obj_visible(obj):
                obj.physicsY(ms)

        # update visible entities
        for layer in self.map_.layers:
            if type(layer) == EntityLayer:
                for sprite in layer.entities:
                    if self.sprite_visible(sprite):
                        sprite.update(ms)

        # adjust offset
        if self.map_.player:
            playerRect = self.map_.player.toPixel()
            if playerRect.left + self.offsetx < self.paddingLeft:
                self.offsetx = self.paddingLeft - playerRect.left
            elif playerRect.right + self.offsetx > self.width - self.paddingRight:
                self.offsetx = int(self.width - self.paddingRight - playerRect.right)

            if playerRect.top + self.offsety < self.paddingTop:
                self.offsety = int(self.paddingTop - playerRect.top)
            elif playerRect.bottom + self.offsety > self.height - self.paddingBottom:
                self.offsety = int(self.height - self.paddingBottom - playerRect.bottom)
            self.clipOffset()

        self.rect.top = - self.offsety
        self.rect.left = - self.offsetx
        self.rect.bottom = - self.offsety + self.height
        self.rect.right = - self.offsetx + self.width

        self.draw()

    def clipOffset(self):
        if self.map_:
            levelWidth = self.map_.pixelWidth()
            levelHeight = self.map_.pixelHeight()
            scrWidth = self.width
            scrHeight = self.height

            if self.offsetx < scrWidth - levelWidth:
                self.offsetx = scrWidth - levelWidth
            if self.offsetx > 0:
                self.offsetx = 0
            if self.offsety < scrHeight - levelHeight:
                self.offsety = scrHeight - levelHeight
            if self.offsety > 0:
                self.offsety = 0

    def draw(self):
        # draw next frame
        if(self.map_):
            self.map_.render(self.surf, (self.offsetx, self.offsety))

    def sprite_visible(self, sprite):
        return self.rect.colliderect(sprite.rect)

    def obj_visible(self, obj):
        if obj.typeName in ['berndman', 'wonderstevie', 'camera',
                            'trigger', 'goal', 'travelPath',
                            'flameThatCannotDies', 'drone']:
            return True
        if not obj.sprite:
            return False
        return self.sprite_visible(obj.sprite)
