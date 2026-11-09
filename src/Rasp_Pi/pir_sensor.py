"""
PIR Motion Sensor interface for HC-SR501 on Raspberry Pi 3B+.
Implements a hysteresis sensing loop:
- Quick pass: returns to IDLE after a short quiet period (PIR_QUIET_SECONDS).
- Continuous detection: if motion is detected continuously beyond PIR_CONTINUOUS_MAX_SECONDS,
  the PIR is completely ignored for PIR_IGNORE_INTERVAL_SECONDS before re-arming.
"""

import time

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
        self.initialized = False

    def initialize(self):
        """Initializes the GPIO pin and performs sensor warmup stabilization."""
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

        print(f"[PIR] Waiting {self.warmup_seconds}s for sensor to stabilize...")
        time.sleep(self.warmup_seconds)
        self.initialized = True
        print("[PIR] HC-SR501 armed and ready.")

    def read(self):
        """Returns True if pin is HIGH (1), False otherwise."""
        if not self.initialized:
            self.initialize()

        if self.backend == "gpiozero" and self.device:
            return int(self.device.value) == 1
        elif self.backend == "RPi.GPIO" and RPI_GPIO_AVAILABLE:
            return GPIO.input(self.pin) == GPIO.HIGH
        return False

    def wait_for_motion(self, poll_interval=0.1):
        """
        Blocks until motion is detected (pin reads HIGH).
        Returns the timestamp of the trigger event.
        """
        if not self.initialized:
            self.initialize()

        while not self.read():
            time.sleep(poll_interval)

        return time.time()

    def wait_for_clear(self, poll_interval=0.2):
        """
        Hysteresis loop after a trigger event:
        1. If pin goes LOW and stays LOW for quiet_seconds -> Clean reset to IDLE.
        2. If pin stays HIGH continuously for continuous_max -> Hysteresis activates,
           PIR is ignored for ignore_interval seconds, then re-arms once sensor drops to LOW.
        """
        start_tracking = time.time()
        last_high = time.time() if self.read() else None

        while True:
            is_high = self.read()
            now = time.time()

            if is_high:
                last_high = now
                continuous_duration = now - start_tracking

                # Continuous detection threshold exceeded!
                if continuous_duration >= self.continuous_max:
                    print(
                        f"\n[HYSTERESIS] Continuous motion detected (> {self.continuous_max:.1f}s)! "
                        f"PIR will be IGNORED for {self.ignore_interval:.1f}s..."
                    )
                    time.sleep(self.ignore_interval)

                    # After ignore interval, ensure pin drops to LOW before re-arming
                    print("[HYSTERESIS] Ignore interval ended. Waiting for sensor to clear to LOW...")
                    low_wait_start = time.time()
                    while self.read():
                        time.sleep(poll_interval)
                        # Safety fallback: don't block indefinitely if hardware pin is stuck
                        if time.time() - low_wait_start > 30.0:
                            print("[HYSTERESIS WARNING] Sensor pin remained HIGH; forcing re-arm.")
                            break
                    break
            else:
                # Pin is LOW (quiet)
                if last_high is None:
                    # Never went high during this check, wait for quiet_seconds
                    time.sleep(self.quiet_seconds)
                    break
                else:
                    quiet_time = now - last_high
                    if quiet_time >= self.quiet_seconds:
                        # Clean quiet reset
                        break

            time.sleep(poll_interval)

        print("[STANDBY] PIR re-armed and ready for next motion event.")

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
