"""sound_manager.py organizes all sounds and plays them accordingly
at the correct time and volume."""
import pygame.mixer
from .paths import resolve_asset_path

class SoundManager:
    _instance = None

    def __init__(self):
        """initializes SoundManager class, including default volume and sounds"""
        pygame.mixer.init()
        pygame.mixer.set_num_channels(20)
        #first channel reserved for music
        #rest of channels reserved for sfx
        self.music_volume = 1
        self.sfx_volume = 1
        self.sounds = []

    def manage(self):
        """updates all sounds"""
        for sound in self.sounds:
            sound.set_volume(self.sfx_volume)
        self.sounds = [s for s in self.sounds if s[1].get_busy()]

    def play_sfx(self, sound):
        """plays a sound """
        sound = pygame.mixer.Sound(resolve_asset_path(sound))
        channel = sound.play()

        if channel is not None:
            sound.set_volume(self.sfx_volume)
            self.sounds.append([sound, channel])

    def play_music(self, music, loop=True):
        """plays music"""
        path = resolve_asset_path(music)
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1 if loop else 0)

    def change_volume(self, volume, st):
        """changes the sound volume"""
        if st == "sfx":
            self.sfx_volume = volume
        else:
            self.music_volume = volume
            pygame.mixer.music.set_volume(self.music_volume)

    @staticmethod
    def get_instance():
        if SoundManager._instance is None:
            SoundManager._instance = SoundManager()
        return SoundManager._instance

