import pygame
import json
import os.path
import random


# TODO: consider defining this elsewhere


class Orientation:
    """Defines, which direction an object/sprite is facing."""

    LEFT = -2
    RIGHT = 2


class Alignment:
    """Defines, which point in a spawned object/sprite is specified as its position."""

    CENTER = 0
    LEFT = 1
    RIGHT = 2
    TOP = 4
    BOTTOM = 8
    TOPLEFT = 5
    TOPRIGHT = 6
    BOTTOMLEFT = 9
    BOTTOMRIGHT = 10


class Frame():
    """Data class for a single animation frame in both orientations"""

    def __init__(self, spriteSheet, data):
        """Create a frame, extracting the image from [spriteSheet] using [data]"""
        x = data['frame']['x']
        y = data['frame']['y']
        w = data['frame']['w']
        h = data['frame']['h']
        rect = pygame.Rect(x,y,w,h)
        self.right = spriteSheet.subsurface(rect)
        self.left = pygame.transform.flip(self.right, True, False)
        self.duration = data['duration']

class Animation():
    """Data class for a single animation consisting of several timed [Frame]s"""

    def __init__(self, frames, data):
        """Create a new animation using the frames specified in [data]."""
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
        """Updates [sprite.image] according to the animation, [sprite.frameNo] and [sprite.frameTime]."""
        if sprite.frameTime > self.frames[sprite.frameNo].duration:
            sprite.frameTime -= self.frames[sprite.frameNo].duration
            sprite.frameNo = (sprite.frameNo + 1) % len(self.frames)
            if sprite.frameNo == 0:
                sprite.on_animationFinished()

        if sprite.orientation == Orientation.LEFT:
            sprite.image = self.frames[sprite.frameNo].left
        else:
            sprite.image = self.frames[sprite.frameNo].right

#TODO: update sprite position in AnimSprite class, not object class - this way, rendering and physics cycle can be further uncoupled
#TODO: reuse sprite sheets

class AnimSprite(pygame.sprite.Sprite):
    """Represents the sprites drawn on the screen."""

    def __init__(self, json_file, position=(0, 0), mirror_h=False,
                 alignment=Alignment.BOTTOMLEFT):
        """Creates a new sprite.

        The information needed is parsed from [json_file], the sprite sheet is loaded.
        """

        super().__init__()

        data = json.load(open(json_file))

        folder = os.path.dirname(json_file) + os.sep

        image = pygame.image.load(folder + data['meta']['image']).convert()
        image.set_colorkey((255, 0, 255))

        self.rect = pygame.rect.Rect(position, (0, 0))
        self.visible = 1

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

        # initialize list for particles
        self.particles = []

    def die(self):
        """Plays the "die" animation, if available, then removes the sprite."""
        if not self.setAnimation('die'):
            self.kill()

    def setAnimation(self, animation, reset=True):
        """Switches to the animation given in [animation].

        If [reset] is True and the given animation is already playing, resets it."""

        if (not reset) and animation == self.currentAnimation.name:
            return True
        if animation in self.animations:
            self.currentAnimation = self.animations[animation]

            self.frameNo = 0
            self.frameTime = 0
            self.currentAnimation.updateFrame(self)
            return True
        return False

    def on_animationFinished(self):
        """Removes the sprite after the "die" animation is played.

        Triggered whenever an animation finished playing."""
        if self.currentAnimation.name == "die":
            self.kill()

    def emit_particles(self, color_list=[(255, 255, 255)]):
        items_to_remove_ = []

        # configuration (to be moved to function args)
        decay = 0.08
        x_velocity = random.randint(0, 20) / 10 - 1
        y_velocity = 2
        particle_radius = random.randint(1, 4)

        # compute intervals for colors
        interval_size = float(particle_radius) / float(len(color_list))
        interval_borders = []
        for ind in range(len(color_list)):
            interval_borders.append(float(ind) * interval_size)
        # create new particle
        self.particles.append([list(self.rect.center),
                               [x_velocity, y_velocity],
                               particle_radius,
                               particle_radius,
                               color_list,
                               interval_borders])
        # compute existing particles
        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= decay
            if particle[2] <= 0:
                items_to_remove_.append(particle)
        # remove nonexistent particles
        for item in items_to_remove_:
            self.particles.remove(item)

    def draw_particles(self, offset, surface):
        for particle in self.particles:
            center = list(map(sum, zip(tuple(particle[0]), offset)))
            # color stuff
            for ind in range(len(particle[4])):
                if particle[2] >= particle[5][ind]:
                    color_index = ind

            pygame.draw.circle(surface,
                               particle[4][color_index],
                               center,
                               particle[2])

    def update(self, ms):
        """Updates the sprite by advancing the animation by [ms] ms."""
        self.frameTime += ms
        self.currentAnimation.updateFrame(self)
        if not self.visible:
            image = pygame.Surface((self.rect.width,
                                    self.rect.height),
                                   flags=pygame.SRCALPHA)
            image.fill((0, 0, 0, 0))
            self.image = image
        return True
