from .game_object import GameObject
from .import config
from .tileset import EntityData


class DialogPlayer(GameObject):
    """A player object to control dialogs."""

    typeName = "dialogplayer"
    collides = False

    def __init__(self, viewport=None, **kwargs):
        """Initializes the dialogplayer."""

        kwargs['size'] = (1, 1)
        self.viewport=viewport
        super().__init__(**kwargs)

    def forward(self, pressed=True):
        """skips to the next sentence in the dialog."""
        if pressed == True:
            self.viewport.next_step += 1

    def quit(self, pressed):
        """Closes the game."""

        if pressed:
            config.running = False


EntityData.registerType(DialogPlayer)
