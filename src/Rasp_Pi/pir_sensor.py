"""
PIR Motion Sensor interface for HC-SR501 on Raspberry Pi 3B+.
Monitors BCM GPIO17 for motion triggers with warmup and clean shutdown.
"""

import time

try:
    import RPi.GPIO as GPIO
    RPI_GPIO_AVAILABLE = True
except ImportError:
    RPI_GPIO_AVAILABLE = False

from src.Rasp_Pi.raspi_config import PIR_PIN, PIR_WARMUP_SECONDS, PIR_COOLDOWN_SECONDS


class PIRSensor:
    def __init__(self, pin=PIR_PIN, warmup_seconds=PIR_WARMUP_SECONDS):
        self.pin = pin
        self.warmup_seconds = warmup_seconds
        self.initialized = False

    def initialize(self):
        """Initializes the GPIO pin and performs sensor warmup stabilization."""
        if not RPI_GPIO_AVAILABLE:
            print("[PIR MOCK] RPi.GPIO not available (running in simulation/host mode).")
            self.initialized = True
            return

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        print(f"[PIR] Sensor on BCM GPIO{self.pin} initializing...")
        print(f"[PIR] Waiting {self.warmup_seconds}s for HC-SR501 to stabilize...")
        time.sleep(self.warmup_seconds)
        self.initialized = True
        print("[PIR] HC-SR501 sensor stabilized and armed.")

    def read(self):
        """Returns True if motion is currently detected (HIGH), False otherwise."""
        if not self.initialized:
            self.initialize()

        if not RPI_GPIO_AVAILABLE:
            return False

        return GPIO.input(self.pin) == GPIO.HIGH

    def wait_for_motion(self, poll_interval=0.1):
        """
        Polls until a LOW -> HIGH edge transition occurs.
        Returns timestamp of the trigger event.
        """
        if not self.initialized:
            self.initialize()

        # Wait until current pin state is LOW (in case of ongoing trigger)
        while self.read():
            time.sleep(poll_interval)

        # Wait for LOW -> HIGH transition
        while not self.read():
            time.sleep(poll_interval)

        return time.time()

    def wait_for_clear(self, timeout=30.0, poll_interval=0.2):
        """
        Waits for PIR pin to return LOW before re-arming.
        """
        start = time.time()
        while self.read():
            time.sleep(poll_interval)
            if time.time() - start > timeout:
                print("[PIR WARNING] Motion signal remained HIGH beyond timeout.")
                break

    def cleanup(self):
        """Cleans up GPIO settings."""
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


if __name__ == "__main__":
    print("=== Standalone PIR Test ===")
    try:
        initialize_pir()
        print("Monitoring for motion... (Ctrl+C to quit)")
        while True:
            t = wait_for_pir_motion()
            print(f"[TRIGGER] Motion detected at {time.strftime('%H:%M:%S', time.localtime(t))}")
            wait_for_pir_clear()
            print("[READY] Sensor cleared and re-armed.")
            time.sleep(PIR_COOLDOWN_SECONDS)
    except KeyboardInterrupt:
        print("\nExiting PIR test...")
    finally:
        cleanup_pir()
