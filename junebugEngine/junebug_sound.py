import pygame

def init():
    pygame.mixer.pre_init(44100, -16, 1, 512)
    pygame.mixer.init()

def load_sound_from_wav(filename):
    return pygame.mixer.Sound(filename)

def load_music(filename):
    return pygame.mixer.music.load(filename)

def play_sound(sound_object, volume=.5, loops=0):
    channel = pygame.mixer.find_channel()
    if channel:
        channel.set_volume(volume)
        channel.play(sound_object, loops=loops)

def fade_in_and_play_music(loops=0,
                           target_volume=1.0,
                           fade_duration=200,
                           fade_tick_duration = 20):
    pygame.mixer.music.set_volume(0.0)
    pygame.mixer.music.play(loops)
    increment = fade_tick_duration / fade_duration
    return True, increment

def update_music_volume(increment):
    new_volume = min(1.0,
                     pygame.mixer.music.get_volume() + increment)
    pygame.mixer.music.set_volume(new_volume)
    if new_volume >= 1.0:
        return False
    return True

def fade_out(fade_duration=1.0):
    pass
