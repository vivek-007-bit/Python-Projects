"""
Sound management system with graceful fallbacks and mute controls.
"""
import os
import pygame
from game.settings import MASTER_VOLUME

class SoundManager:
    def __init__(self, assets_dir=None):
        self.mixer_available = False
        self.muted = False
        self.volume = MASTER_VOLUME
        self.sounds = {}

        if assets_dir is None:
            base = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.path.join(os.getcwd(), "game")
            assets_dir = os.path.join(base, "assets", "sounds")
        self.assets_dir = assets_dir

        self._init_mixer()
        self._load_sounds()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.mixer_available = True
        except Exception as e:
            print(f"[SoundManager] Audio mixer initialization failed: {e}. Running in silent mode.")
            self.mixer_available = False

    def _load_sounds(self):
        sound_keys = ["flap", "point", "hit", "die"]
        for key in sound_keys:
            self.sounds[key] = None
            if not self.mixer_available:
                continue

            file_path = os.path.join(self.assets_dir, f"{key}.ogg")
            if os.path.exists(file_path):
                try:
                    snd = pygame.mixer.Sound(file_path)
                    snd.set_volume(self.volume)
                    self.sounds[key] = snd
                except Exception as e:
                    print(f"[SoundManager] Failed to load sound '{key}.ogg': {e}")

    def play(self, sound_name):
        if self.muted or not self.mixer_available:
            return
        snd = self.sounds.get(sound_name)
        if snd is not None:
            try:
                snd.play()
            except Exception as e:
                print(f"[SoundManager] Error playing sound '{sound_name}': {e}")

    def play_flap(self):
        self.play("flap")

    def play_point(self):
        self.play("point")

    def play_hit(self):
        self.play("hit")

    def play_die(self):
        self.play("die")

    def toggle_mute(self):
        self.muted = not self.muted
        return self.muted

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        for snd in self.sounds.values():
            if snd is not None:
                try:
                    snd.set_volume(self.volume)
                except Exception:
                    pass
