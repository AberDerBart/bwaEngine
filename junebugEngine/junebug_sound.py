import pygame


def load_sound_from_wav(filename):
    return pygame.mixer.Sound(filename)


def play_sound(sound_object, volume=.5):
    channel = pygame.mixer.find_channel()
    if channel:
        channel.set_volume(volume)
        channel.play(sound_object)
