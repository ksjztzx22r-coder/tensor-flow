import threading
from pathlib import Path

import pygame

from Rasp_Pi.raspi_config import *

# ==========================================================
# Initialize Audio
# ==========================================================

pygame.mixer.init()

# ==========================================================
# Audio Dictionary
# ==========================================================

AUDIO_FILES = {

    "elephant": str(ELEPHANT_AUDIO),

    "wildboar": str(BOAR_AUDIO),

    "monkey": str(MONKEY_AUDIO)

}

# ==========================================================
# Audio Player
# ==========================================================

class AudioPlayer:

    def __init__(self):

        self.lock = threading.Lock()

        self.current_sound = None

    def play(self, label):

        if label not in AUDIO_FILES:

            return

        sound = AUDIO_FILES[label]

        if not Path(sound).exists():

            print(f"[WARNING] Audio file not found: {sound}")

            return

        with self.lock:

            if (

                self.current_sound == label

                and pygame.mixer.music.get_busy()

        ):

                return

        pygame.mixer.music.stop()

        pygame.mixer.music.load(sound)

        pygame.mixer.music.play()

        self.current_sound = label

    def stop(self):

        pygame.mixer.music.stop()

        self.current_sound = None

    def is_playing(self):

        return pygame.mixer.music.get_busy()


player = AudioPlayer()

# ==========================================================
# Public API
# ==========================================================

def play_audio(label):

    player.play(label)


def stop_audio():

    player.stop()


def audio_busy():

    return player.is_playing()

# ==========================================================
# Standalone Test
# ==========================================================

if __name__ == "__main__":

    while True:

        animal = input(

            "Animal (elephant/wildboar/monkey/quit): "

        ).strip().lower()

        if animal == "quit":

            break

        play_audio(animal)

    stop_audio()