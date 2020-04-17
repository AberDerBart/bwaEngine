from .sprite import Orientation
from .game_object import GameObject, Direction
from .junebug_sound import load_sound_from_wav, play_sound


class MovingObject(GameObject):
    """A controllable GameObject

    can react to edges, walls and other GameObjects"""

    acc = 500
    speed = 100

    def __init__(self, **kwargs):
        """Initializes a MovingObject"""

        super().__init__(**kwargs)

        # sound
        self.jump_sound = load_sound_from_wav('sound/jump.wav')

        self.jumpTime = 0
        self.jumping = False

        self.idle()

    def run_left(self):
        """Starts accelerating [self] to the left until [self.speed] is reached.

        Also sets the orientation to left and sets the 'run' animation on the corresponding sprite"""

        self.targetSpeed = -self.speed
        self.orientation = Orientation.LEFT
        # TODO: make sprite check for its orientation on every frame
        self.updateSpritePosition()
        if self.sprite:
            self.sprite.setAnimation('run')

    def run_right(self):
        """Starts accelerating [self] to the right until [self.speed] is reached.

        Also sets the orientation to right and sets the 'run' animation on the corresponding sprite"""

        self.targetSpeed = -self.speed
        self.targetSpeed = self.speed
        self.orientation = Orientation.RIGHT
        # TODO: make sprite check for its orientation on every frame
        self.updateSpritePosition()
        if self.sprite:
            self.sprite.setAnimation('run')

    def jump(self, hold=True):
        """Makes the object jump.

        If [hold] is False, stops accelerating upwards."""

        if self.on_ground and hold:
            play_sound(self.jump_sound, volume=.3)
            self.jumping = True
            self.jumpTime = 0
        if not hold:
            self.jumping = False

    def idle(self):
        """Make the object stop moving.

        Also sets the animation of the corresponding sprite to 'idle'"""

        self.targetSpeed = 0
        if self.sprite:
            self.sprite.setAnimation('idle')

    def on_edge(self, direction):
        """Does something when the object reaches and edge.

        Override this to implement custom behaviour."""

        pass

    def die(self):
        """Removes the object from physics and rendering.

        Override this to implement custom behaviour on death.
        Don't forget to call super().die()"""

        self.targetSpeed = 0
        super().die()

    def update(self, ms, frameIndex):
        """Updates the object.

        Applies physics of running, jumping, etc. and calls GameObject.update"""

        # handle horizontal movement
        if self.targetSpeed > self.vx:
            self.vx = min(self.vx + self.acc * ms / 1000., self.targetSpeed)
        elif self.targetSpeed < self.vx:
            self.vx = max(self.vx - self.acc * ms / 1000., self.targetSpeed)

        # handle jumping
        if self.jumpTime < 250:
            self.jumpTime += ms
            if self.jumping:
                # stay rising constantly, until the maximal jumptime has passed
                self.vy = -200
            else:
                # decellerate jump with twice the speed,
                # if jump button was released
                if self.vy < 0:
                    self.simulate_gravity(ms)

        # edge detection
        if self.on_ground and self.vx != 0:
            groundY = self.bottom

            if self.vx > 0:
                direction = Direction.RIGHT
                groundX = self.right
            else:
                direction = Direction.LEFT
                groundX = self.left

            nextTile = self.world.tileAt((groundX, groundY))

            if not nextTile or not nextTile.collides():
                self.on_edge(direction)

        super().update(ms, frameIndex)
