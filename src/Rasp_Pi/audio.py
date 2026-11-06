"""
Audio playback controller using Pygame Mixer for animal deterrent sounds.
Thread-safe with maximum playback duration timer to preserve power.
"""

import threading
import time
from pathlib import Path
import pygame

from src.Rasp_Pi.raspi_config import (
    ELEPHANT_AUDIO,
    BOAR_AUDIO,
    MONKEY_AUDIO,
    AUDIO_PLAYBACK_MAX_SECONDS,
)

pygame.mixer.init()

AUDIO_FILES = {
    "elephant": str(ELEPHANT_AUDIO),
    "wildboar": str(BOAR_AUDIO),
    "monkey": str(MONKEY_AUDIO)
}


class AudioPlayer:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_sound = None
        self.stop_timer = None

    def play(self, label):
        if label not in AUDIO_FILES:
            return

        sound = AUDIO_FILES[label]
        if not Path(sound).exists():
            print(f"[AUDIO WARNING] Sound file not found: {sound}")
            return

        with self.lock:
            # Cancel any pending auto-stop timer
            if self.stop_timer is not None:
                self.stop_timer.cancel()
                self.stop_timer = None

            pygame.mixer.music.stop()
            pygame.mixer.music.load(sound)
            pygame.mixer.music.play()
            self.current_sound = label
            print(f"[AUDIO] Playing deterrence audio for: {label}")

            # Enforce max duration to protect battery and prevent infinite loops
            self.stop_timer = threading.Timer(AUDIO_PLAYBACK_MAX_SECONDS, self.stop)
            self.stop_timer.daemon = True
            self.stop_timer.start()

    def stop(self):
        with self.lock:
            if self.stop_timer is not None:
                self.stop_timer.cancel()
                self.stop_timer = None
            pygame.mixer.music.stop()
            self.current_sound = None

    def is_playing(self):
        return pygame.mixer.music.get_busy()


player = AudioPlayer()

def play_audio(label):
    player.play(label)

def stop_audio():
    player.stop()

def audio_busy():
    return player.is_playing()


if __name__ == "__main__":
    print("=== Standalone Audio Test ===")
    print("Testing elephant deterrence...")
    play_audio("elephant")
    time.sleep(3)
    stop_audio()
    print("Audio test finished.")
