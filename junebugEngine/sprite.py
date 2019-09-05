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

        allFramesRight = []
        allFramesLeft = []

        for frame in data['frames']:
            x = frame['frame']['x']
            y = frame['frame']['y']
            w = frame['frame']['w']
            h = frame['frame']['h']

            rect = pygame.Rect(x, y, w, h)
            self.rect.width = int(w)
            self.rect.height = int(h)
            frameImg = image.subsurface(rect)
            duration = frame['duration']

            allFramesRight.append((frameImg, duration))
            allFramesLeft.append((pygame.transform.flip(frameImg,
                                                        True, False),
                                  duration))

        self.animations = {
            Orientation.LEFT: {},
            Orientation.RIGHT: {}
        }

        for animation in data['meta']['frameTags']:
            name = animation['name']
            first = animation['from']
            last = animation['to']
            direction = animation['direction']

            framesRight = allFramesRight[first:last+1]
            framesLeft = allFramesLeft[first:last+1]

            self.animations[Orientation.RIGHT][name] = (framesRight, direction)
            self.animations[Orientation.LEFT][name] = (framesLeft, direction)

        # adjust position to alignment

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
        pass

    def setAnimation(self, animation, reset=True):
        if (not reset) and animation == self.currentAnimationName:
            return True
        if animation in self.animations[self.orientation]:
            self.currentAnimationName = animation
            self.currentAnimation = self.animations[self.orientation][animation]

            if(self.currentAnimation[1] == 'reverse'):
                self.frameNo = len(self.currentAnimation[0]) - 1
            else:
                self.frameNo = 0

            self.frameTime = 0
            self.direction = self.currentAnimation[1]
            self.image = self.currentAnimation[0][self.frameNo][0]
            return True

    def animationDuration(self, animation):
        return sum([frame[1] for frame in self.animations[self.orientation].get(animation, [])[0]])

    def on_animationFinished(self):
        if self.currentAnimationName == "die":
            self.kill()

    def update(self, ms):
        self.frameTime = self.frameTime + ms
        curr = self.currentAnimation[0][self.frameNo]
        direction = self.currentAnimation[1]
        if self.frameTime > curr[1]:
            self.frameTime = self.frameTime - curr[1]
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
        self.image = self.currentAnimation[0][self.frameNo][0]
