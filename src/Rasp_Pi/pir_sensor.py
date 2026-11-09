"""
PIR Motion Sensor interface for HC-SR501 on Raspberry Pi 3B+.
Implements robust hysteresis sensing loop:
- Startup baseline calibration: Guarantees initial state is NO MOTION (0).
- Rising-edge triggering: Requires clean 0 -> 1 transition with debounce.
- Quick pass: Resets to IDLE after a short quiet window (PIR_QUIET_SECONDS).
- Continuous detection suppression: If motion persists continuously for >= PIR_CONTINUOUS_MAX_SECONDS,
  PIR is completely ignored for PIR_IGNORE_INTERVAL_SECONDS before re-arming.
"""

import time
import sys

try:
    from gpiozero import DigitalInputDevice
    GPIO_BACKEND = "gpiozero"
except ImportError:
    GPIO_BACKEND = "RPi.GPIO"

try:
    import RPi.GPIO as GPIO
    RPI_GPIO_AVAILABLE = True
except ImportError:
    RPI_GPIO_AVAILABLE = False

from src.Rasp_Pi.raspi_config import (
    PIR_PIN,
    PIR_WARMUP_SECONDS,
    PIR_QUIET_SECONDS,
    PIR_CONTINUOUS_MAX_SECONDS,
    PIR_IGNORE_INTERVAL_SECONDS,
)


class PIRSensor:
    def __init__(
        self,
        pin=PIR_PIN,
        warmup_seconds=PIR_WARMUP_SECONDS,
        quiet_seconds=PIR_QUIET_SECONDS,
        continuous_max=PIR_CONTINUOUS_MAX_SECONDS,
        ignore_interval=PIR_IGNORE_INTERVAL_SECONDS,
    ):
        self.pin = pin
        self.warmup_seconds = warmup_seconds
        self.quiet_seconds = quiet_seconds
        self.continuous_max = continuous_max
        self.ignore_interval = ignore_interval
        self.device = None
        self.backend = None
        self.initialized = False

    def initialize(self):
        """Initializes GPIO and performs baseline calibration to guarantee clean NO MOTION state."""
        if self.initialized:
            return

        print(f"[PIR] Sensor on BCM GPIO{self.pin} initializing...")
        try:
            from gpiozero import DigitalInputDevice
            self.device = DigitalInputDevice(self.pin, pull_up=False)
            self.backend = "gpiozero"
        except Exception:
            if RPI_GPIO_AVAILABLE:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                self.backend = "RPi.GPIO"
            else:
                self.backend = "mock"

        # Baseline Calibration: Ensure initial state is strictly NO MOTION (0)
        print("[PIR] Calibrating sensor baseline (guaranteeing initial NO MOTION state)...")
        if self.read():
            print("[PIR] Sensor pin is currently HIGH. Waiting for sensor to settle to 0...")
            settle_start = time.time()
            while self.read():
                time.sleep(0.2)
                if time.time() - settle_start > 45.0:
                    print("[PIR WARNING] Sensor pin hold-time is long; proceeding with baseline verification.")
                    break

        # Verify at least 2 continuous seconds of clean quiet baseline (0)
        print("[PIR] Verifying 2s clean quiet baseline...")
        quiet_start = time.time()
        while time.time() - quiet_start < 2.0:
            if self.read():
                quiet_start = time.time()
            time.sleep(0.1)

        self.initialized = True
        print("[PIR] Clean baseline established: State 0 (NO MOTION). Sensor armed and ready.")

    def read(self):
        """Returns True if pin is HIGH (1), False otherwise."""
        if self.backend == "gpiozero" and self.device:
            return int(self.device.value) == 1
        elif self.backend == "RPi.GPIO" and RPI_GPIO_AVAILABLE:
            return GPIO.input(self.pin) == GPIO.HIGH
        return False

    def wait_for_motion(self, poll_interval=0.05):
        """
        Blocks until a verified rising-edge (0 -> 1) motion event occurs.
        Returns the timestamp of the trigger event.
        """
        if not self.initialized:
            self.initialize()

        # Step 1: Ensure pin is LOW (0) before accepting a new trigger
        while self.read():
            time.sleep(poll_interval)

        # Step 2: Wait for 0 -> 1 transition with 30ms debounce
        while True:
            if self.read():
                time.sleep(0.03)
                if self.read():
                    return time.time()
            time.sleep(poll_interval)

    def wait_for_clear(self, poll_interval=0.1):
        """
        Hysteresis loop after a trigger event:
        1. If motion clears (pin is 0) and stays 0 for quiet_seconds -> Clean reset to IDLE.
        2. If motion persists continuously for continuous_max -> Hysteresis activates,
           PIR is ignored for ignore_interval seconds, then re-arms once sensor drops to 0.
        """
        start_tracking = time.time()
        last_high = time.time() if self.read() else None

        while True:
            is_high = self.read()
            now = time.time()

            if is_high:
                last_high = now
                continuous_duration = now - start_tracking

                # Continuous presence threshold exceeded!
                if continuous_duration >= self.continuous_max:
                    print(
                        f"\n[HYSTERESIS] Continuous motion detected (> {self.continuous_max:.1f}s)! "
                        f"PIR will be IGNORED for {self.ignore_interval:.1f}s..."
                    )
                    time.sleep(self.ignore_interval)

                    # After ignore interval, ensure pin drops to LOW (0) before re-arming
                    print("[HYSTERESIS] Ignore window ended. Waiting for sensor to clear to 0...")
                    low_wait_start = time.time()
                    while self.read():
                        time.sleep(poll_interval)
                        # Safety fallback: don't hang if hardware pin stays stuck
                        if time.time() - low_wait_start > 30.0:
                            print("[HYSTERESIS WARNING] Sensor pin remained HIGH; forcing re-arm.")
                            break

                    # Require 1 second of confirmed LOW before exiting
                    time.sleep(1.0)
                    break
            else:
                # Pin is LOW (0)
                if last_high is None:
                    time.sleep(self.quiet_seconds)
                    break
                else:
                    quiet_time = now - last_high
                    if quiet_time >= self.quiet_seconds:
                        # Clean quiet reset
                        break

            time.sleep(poll_interval)

        print("[STANDBY] PIR re-armed. Waiting for next motion event...")

    def cleanup(self):
        """Cleans up GPIO settings."""
        if self.device:
            try:
                self.device.close()
            except Exception:
                pass
            self.device = None

        if RPI_GPIO_AVAILABLE:
            try:
                GPIO.cleanup(self.pin)
            except Exception:
                pass

        self.initialized = False
        print("[PIR] GPIO cleaned up.")


# Singleton instance
pir_sensor = PIRSensor()

def initialize_pir():
    pir_sensor.initialize()

def motion_detected():
    return pir_sensor.read()

def wait_for_pir_motion():
    return pir_sensor.wait_for_motion()

def wait_for_pir_clear():
    pir_sensor.wait_for_clear()

def cleanup_pir():
    pir_sensor.cleanup()
