import pygame
import json
import os.path


# TODO: consider defining this elsewhere


class Orientation:
    LEFT = -2
    RIGHT = 2


class Alignment:
    CENTER = 0
    LEFT = 1
    RIGHT = 2
    TOP = 4
    BOTTOM = 8
    TOPLEFT = 5
    TOPRIGHT = 6
    BOTTOMLEFT = 9
    BOTTOMRIGHT = 10


# TODO: refactor the AnimSprite class, moving animations to a seperate class

class Frame():
    def __init__(self, spriteSheet, data):
        x = data['frame']['x']
        y = data['frame']['y']
        w = data['frame']['w']
        h = data['frame']['h']
        rect = pygame.Rect(x,y,w,h)
        self.right = spriteSheet.subsurface(rect)
        self.left = pygame.transform.flip(self.right, True, False)
        self.duration = data['duration']

class Animation():
    def __init__(self, frames, data):
        self.name = data['name']
        direction = data['direction']

        first = data['from']
        last = data['to']
        if direction == 'reverse':
            self.frames = list(reversed(frames[first:last+1]))
        elif direction == 'pingpong':
            self.frames = frames[first:last+1] + \
              list(reversed(frames[first:last]))
        else:
            self.frames = frames[first:last+1]

        self.duration = sum(frame.duration for frame in self.frames)

    def updateFrame(self, sprite):
        if sprite.frameTime > self.frames[sprite.frameNo].duration:
            sprite.frameTime -= self.frames[sprite.frameNo].duration
            sprite.frameNo = (sprite.frameNo + 1) % len(self.frames)
            if sprite.frameNo == 0:
                sprite.on_animationFinished()

        if sprite.orientation == Orientation.LEFT:
            sprite.image = self.frames[sprite.frameNo].left
        else:
            sprite.image = self.frames[sprite.frameNo].right

class AnimSprite(pygame.sprite.Sprite):
    typeName = None

    def __init__(self, json_file, position=(0, 0), mirror_h=False,
                 alignment=Alignment.BOTTOMLEFT):
        super().__init__()

        data = json.load(open(json_file))

        folder = os.path.dirname(json_file) + os.sep

        image = pygame.image.load(folder + data['meta']['image']).convert()
        image.set_colorkey((255, 0, 255))

        self.rect = pygame.rect.Rect(position, (0, 0))

        # split into frames
        allFrames = []

        for frame in data['frames']:
            allFrames.append(Frame(image, frame))

        # generate animations
        self.animations = {}

        for animationData in data['meta']['frameTags']:
            animation = Animation(allFrames, animationData)
            self.animations[animation.name] = animation

        # adjust size and position to alignment
        if allFrames:
            self.rect.size = allFrames[0].right.get_size()

        if alignment & Alignment.BOTTOM:
            self.rect.y -= self.rect.height
        elif not (alignment & Alignment.TOP):
            self.rect.y -= self.rect.height / 2
        if alignment & Alignment.RIGHT:
            self.rect.x -= self.rect.width
        elif not (alignment & Alignment.LEFT):
            self.rect.x -= self.rect.width / 2

        if mirror_h:
            self.orientation = Orientation.LEFT
        else:
            self.orientation = Orientation.RIGHT
        self.setAnimation(data['meta']['frameTags'][0]['name'])

    def die(self):
        if not self.setAnimation('die'):
            self.kill()
        self.on_death()

    def on_death(self):
        self.kill()

    def setAnimation(self, animation, reset=True):
        if (not reset) and animation == self.currentAnimation.name:
            return True
        if animation in self.animations:
            self.currentAnimation = self.animations[animation]

            self.frameNo = 0
            self.frameTime = 0
            self.currentAnimation.updateFrame(self)
            return True
        return False

    def animationDuration(self, animation):
        return animation.duration

    def on_animationFinished(self):
        if self.currentAnimation.name == "die":
            self.kill()

    def update(self, ms):
        self.frameTime += ms
        self.currentAnimation.updateFrame(self)
        return True
        curr = self.currentAnimation[0][self.frameNo]
        direction = self.currentAnimation[1]
        if self.frameTime > curr['duration']:
            self.frameTime = self.frameTime - curr['duration']
            if self.direction == 'pingpong':
                self.frameNo = self.frameNo + 1
                if self.frameNo == len(self.currentAnimation[0]) - 1:
                    self.direction = 'pingpong_r'
            elif self.direction == 'pingpong_r':
                self.frameNo = self.frameNo - 1
                if self.frameNo == 0:
                    self.direction = 'pingpong'
            elif self.direction == 'reverse':
                self.frameNo = (self.frameNo - 1) % len(self.currentAnimation[0])
                if (self.frameNo == len(self.currentAnimation[0]) - 1):
                    self.on_animationFinished()
            else:
                self.frameNo = (self.frameNo + 1) % len(self.currentAnimation[0])
                if self.frameNo == 0:
                    self.on_animationFinished()
        self.image = self.currentAnimation[0][self.frameNo][self.orientation]
