"""
PIR Motion Sensor interface for HC-SR501 on Raspberry Pi 3B+.
Monitors BCM GPIO17 for motion triggers with continuous Trigger <-> No Trigger state cycling.
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

from src.Rasp_Pi.raspi_config import PIR_PIN, PIR_WARMUP_SECONDS, PIR_COOLDOWN_SECONDS


class PIRSensor:
    def __init__(self, pin=PIR_PIN, warmup_seconds=PIR_WARMUP_SECONDS, timeout_seconds=PIR_COOLDOWN_SECONDS):
        self.pin = pin
        self.warmup_seconds = warmup_seconds
        self.timeout_seconds = timeout_seconds
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

    def wait_for_clear(self, timeout=None, poll_interval=0.2):
        """
        Waits until there has been no motion for timeout_seconds.
        """
        if timeout is None:
            timeout = self.timeout_seconds

        last_motion = time.time()
        while True:
            if self.read():
                last_motion = time.time()
            elif time.time() - last_motion >= timeout:
                break
            time.sleep(poll_interval)

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
