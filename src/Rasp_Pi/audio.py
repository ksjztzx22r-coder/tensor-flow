"""
Audio playback controller for animal deterrent sounds on Raspberry Pi.
Features:
- Primary backend on Raspberry Pi / Linux: Native ALSA `aplay` (auto-detects USB sound card).
- Fallback backend (Windows / SDL): `pygame.mixer.Sound`.
- Non-blocking, thread-safe with automatic duration cutoff to protect battery.
"""

import os
import shutil
import subprocess
import threading
import time
from pathlib import Path

from src.Rasp_Pi.raspi_config import (
    ELEPHANT_AUDIO,
    BOAR_AUDIO,
    MONKEY_AUDIO,
    AUDIO_PLAYBACK_MAX_SECONDS,
)

AUDIO_FILES = {
    "elephant": str(ELEPHANT_AUDIO),
    "wildboar": str(BOAR_AUDIO),
    "monkey": str(MONKEY_AUDIO),
}

# Check if native Linux ALSA aplay is available
APLAY_BIN = shutil.which("aplay")

# Check Pygame availability for fallback
PYGAME_AVAILABLE = False
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False


def find_usb_alsa_device():
    """
    Scans `aplay -l` to find the exact ALSA device string for a USB speaker.
    Returns device string (e.g., 'plughw:CARD=Device,DEV=0' or 'default').
    """
    if not APLAY_BIN:
        return "default"

    try:
        out = subprocess.check_output([APLAY_BIN, "-l"], stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
        # Look for USB card names like "Device", "USB", "Headset", "DAC"
        for line in out.splitlines():
            if "card" in line and ("USB" in line or "Device" in line or "Audio" in line):
                # Extract card number or name, e.g. "card 1: Device [USB Audio Device]"
                parts = line.split(":")
                card_part = parts[0].strip() # "card 1"
                card_num = card_part.replace("card", "").strip()
                return f"plughw:{card_num},0"
    except Exception:
        pass

    return "default"


class AudioPlayer:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_sound = None
        self.process = None
        self.pygame_sound = None
        self.stop_timer = None
        self.usb_device = find_usb_alsa_device() if APLAY_BIN else None

    def play(self, label):
        if label not in AUDIO_FILES:
            return

        sound_path = AUDIO_FILES[label]
        if not Path(sound_path).exists():
            print(f"[AUDIO WARNING] Sound file not found: {sound_path}")
            return

        with self.lock:
            # Stop any currently playing audio
            self._stop_internal()

            self.current_sound = label
            print(f"[AUDIO] Triggering deterrence audio for '{label}' -> {Path(sound_path).name}")

            # Method 1: Native Linux aplay (Most reliable on Raspberry Pi with USB speakers)
            if APLAY_BIN:
                try:
                    cmd = [APLAY_BIN]
                    if self.usb_device and self.usb_device != "default":
                        cmd.extend(["-D", self.usb_device])
                    cmd.append(sound_path)

                    self.process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except Exception as e:
                    print(f"[AUDIO WARNING] aplay execution failed ({e}), falling back to pygame.")
                    self.process = None

            # Method 2: Pygame Sound (Fallback)
            if self.process is None and PYGAME_AVAILABLE:
                try:
                    self.pygame_sound = pygame.mixer.Sound(sound_path)
                    self.pygame_sound.play()
                except Exception as e:
                    print(f"[AUDIO ERROR] Pygame playback failed: {e}")

            # Enforce max duration cutoff to protect battery
            self.stop_timer = threading.Timer(AUDIO_PLAYBACK_MAX_SECONDS, self.stop)
            self.stop_timer.daemon = True
            self.stop_timer.start()

    def _stop_internal(self):
        """Internal stop without lock."""
        if self.stop_timer is not None:
            self.stop_timer.cancel()
            self.stop_timer = None

        if self.process is not None:
            try:
                self.process.terminate()
                self.process.wait(timeout=0.5)
            except Exception:
                pass
            self.process = None

        if self.pygame_sound is not None:
            try:
                self.pygame_sound.stop()
            except Exception:
                pass
            self.pygame_sound = None

        self.current_sound = None

    def stop(self):
        with self.lock:
            self._stop_internal()

    def is_playing(self):
        if self.process is not None:
            return self.process.poll() is None
        if self.pygame_sound is not None and PYGAME_AVAILABLE:
            return pygame.mixer.get_busy()
        return False


player = AudioPlayer()

def play_audio(label):
    player.play(label)

def stop_audio():
    player.stop()

def audio_busy():
    return player.is_playing()


if __name__ == "__main__":
    print("=" * 60)
    print("          STANDALONE AUDIO HARDWARE TEST")
    print("=" * 60)
    if APLAY_BIN:
        print(f"[AUDIO INFO] Linux ALSA 'aplay' detected at: {APLAY_BIN}")
        print(f"[AUDIO INFO] Target device string: {player.usb_device}")
    else:
        print("[AUDIO INFO] Using Pygame Mixer backend.")

    print("\n[TEST] Playing elephant deterrence audio for 5 seconds...")
    play_audio("elephant")
    time.sleep(5)
    stop_audio()
    print("[TEST COMPLETE] If you did not hear sound, see the ALSA sound card guide.")
